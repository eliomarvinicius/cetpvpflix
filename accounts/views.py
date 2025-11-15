from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.db import models

from catalog.models import Favorite
from reviews.models import Review
from .forms import CustomUserCreationForm, ProfileUpdateForm

User = get_user_model()


class CustomLoginView(LoginView):
    """
    View customizada para login
    """
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        messages.success(self.request, f'Bem-vindo de volta, {self.request.user.first_name or self.request.user.username}!')
        return reverse_lazy('catalog:home')


class RegisterView(CreateView):
    """
    View para registro de novo usuário
    """
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('catalog:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        
        # Fazer login automático após registro
        login(self.request, self.object)
        
        messages.success(
            self.request, 
            f'Conta criada com sucesso! Bem-vindo ao CETPVPFLIX, {username}!'
        )
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Perfil do usuário com estatísticas
    """
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Estatísticas do usuário
        context['stats'] = {
            'total_favorites': Favorite.objects.filter(user=user).count(),
            'total_reviews': Review.objects.filter(user=user).count(),
            'average_rating': Review.objects.filter(user=user).aggregate(
                avg=models.Avg('rating')
            )['avg'] or 0,
        }
        
        # Favoritos recentes
        context['recent_favorites'] = Favorite.objects.filter(
            user=user
        ).select_related('media').order_by('-created_at')[:6]
        
        # Avaliações recentes
        context['recent_reviews'] = Review.objects.filter(
            user=user
        ).select_related('media').order_by('-created_at')[:6]
        
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Editar perfil do usuário
    """
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)
