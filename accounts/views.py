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
        
        # Favoritos
        favorites = Favorite.objects.filter(user=user)
        context['favorites'] = favorites[:12]  # Primeiros 12 para exibir
        context['favorites_count'] = favorites.count()
        
        # Avaliações
        user_reviews = Review.objects.filter(user=user).select_related('media')
        context['user_reviews'] = user_reviews[:10]  # Primeiras 10 para exibir
        context['reviews_count'] = user_reviews.count()
        
        # Solicitações de conteúdo
        from catalog.models import ContentRequest
        content_requests = ContentRequest.objects.filter(user=user)
        context['content_requests'] = content_requests[:6]  # Primeiras 6 para exibir
        context['requests_count'] = content_requests.count()
        
        # Likes recebidos nas avaliações
        context['likes_received'] = sum(review.likes.count() for review in user_reviews)
        
        # Atividade recente (combinando favoritos, reviews e solicitações)
        recent_activities = []
        
        # Favoritos recentes
        for fav in favorites.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'favorite',
                'description': f'Adicionou "{fav.media.title}" aos favoritos',
                'details': f'Filme' if fav.media.media_type == 'movie' else 'Série',
                'timestamp': fav.created_at
            })
        
        # Reviews recentes
        for review in user_reviews.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'review',
                'description': f'Avaliou "{review.media.title}"',
                'details': f'{review.rating} estrelas - {review.comment[:50]}...' if review.comment else f'{review.rating} estrelas',
                'timestamp': review.created_at
            })
        
        # Solicitações recentes
        for request in content_requests.order_by('-created_at')[:3]:
            recent_activities.append({
                'type': 'request',
                'description': f'Solicitou "{request.title}"',
                'details': f'Status: {request.get_status_display()}',
                'timestamp': request.created_at
            })
        
        # Ordenar atividades por data e pegar as 10 mais recentes
        context['recent_activities'] = sorted(
            recent_activities, 
            key=lambda x: x['timestamp'], 
            reverse=True
        )[:10]
        
        # Perfil do usuário (se tiver model de perfil separado, senão usar dados do User)
        context['profile'] = user  # ou user.profile se tiver um modelo Profile separado
        
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
