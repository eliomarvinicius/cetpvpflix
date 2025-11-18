from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.db.models import Avg

from .models import Review, ReviewLike
from catalog.models import Media


class AddReviewView(LoginRequiredMixin, CreateView):
    """
    Adicionar avaliação
    """
    model = Review
    template_name = 'reviews/add_review.html'
    fields = ['rating', 'comment']
    
    def dispatch(self, request, *args, **kwargs):
        self.media = get_object_or_404(Media, id=kwargs['media_id'])
        
        # Verificar se o usuário já avaliou
        if Review.objects.filter(user=request.user, media=self.media).exists():
            messages.error(request, 'Você já avaliou este conteúdo.')
            return redirect('catalog:media_detail', pk=self.media.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.media = self.media
        
        messages.success(
            self.request,
            f'Sua avaliação para "{self.media.title}" foi adicionada com sucesso!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('catalog:media_detail', kwargs={'pk': self.media.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media'] = self.media
        return context


class EditReviewView(LoginRequiredMixin, UpdateView):
    """
    Editar avaliação
    """
    model = Review
    template_name = 'reviews/edit_review.html'
    fields = ['rating', 'comment']
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'Sua avaliação para "{self.object.media.title}" foi atualizada!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('catalog:media_detail', kwargs={'pk': self.object.media.id})


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    """
    Excluir avaliação
    """
    model = Review
    template_name = 'reviews/delete_review.html'
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('catalog:media_detail', kwargs={'pk': self.object.media.id})
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        media_id = self.object.media.id
        media_title = self.object.media.title
        
        messages.success(
            request,
            f'Sua avaliação para "{media_title}" foi removida.'
        )
        
        return super().delete(request, *args, **kwargs)


class MediaReviewsView(ListView):
    """
    Lista de avaliações de um filme/série
    """
    model = Review
    template_name = 'reviews/media_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.media = get_object_or_404(Media, id=kwargs['media_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Review.objects.filter(
            media=self.media,
            is_active=True
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media'] = self.media
        
        # Estatísticas das avaliações
        reviews = self.get_queryset()
        context['total_reviews'] = reviews.count()
        context['average_rating'] = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Distribuição de notas
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = reviews.filter(rating=i).count()
        context['rating_distribution'] = rating_distribution
        
        return context


# Function-based views para AJAX
@login_required
def ajax_add_review(request):
    """
    Adicionar avaliação via AJAX
    """
    if request.method == 'POST':
        media_id = request.POST.get('media_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        try:
            media = Media.objects.get(id=media_id)
            
            # Verificar se já existe avaliação
            if Review.objects.filter(user=request.user, media=media).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Você já avaliou este conteúdo.'
                })
            
            # Criar avaliação
            review = Review.objects.create(
                user=request.user,
                media=media,
                rating=int(rating),
                comment=comment
            )
            
            # Calcular nova média
            avg_rating = media.reviews.aggregate(avg=Avg('rating'))['avg']
            
            return JsonResponse({
                'success': True,
                'message': 'Avaliação adicionada com sucesso!',
                'review_id': review.id,
                'new_average': round(avg_rating, 1) if avg_rating else 0,
                'total_reviews': media.reviews.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido'
    })


@login_required
def ajax_like_review(request, review_id):
    """
    Like/Unlike em avaliação via AJAX
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido'
        })
    
    review = get_object_or_404(Review, id=review_id)
    
    # Não permitir curtir própria avaliação
    if review.user == request.user:
        return JsonResponse({
            'success': False,
            'error': 'Você não pode curtir sua própria avaliação.',
            'is_own_review': True
        })
    
    like, created = ReviewLike.objects.get_or_create(
        user=request.user,
        review=review
    )
    
    if not created:
        like.delete()
        liked = False
        action = 'unliked'
    else:
        liked = True
        action = 'liked'
    
    total_likes = review.likes.count()
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'action': action,
        'total_likes': total_likes,
        'message': 'Like adicionado!' if liked else 'Like removido!'
    })
