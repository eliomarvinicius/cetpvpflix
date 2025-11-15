from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.urls import reverse_lazy

from .models import Media, Genre, Favorite, ContentRequest
from reviews.models import Review
from services.tmdb_service import tmdb_service


class HomeView(ListView):
    """
    Página inicial com filmes e séries populares
    """
    model = Media
    template_name = 'catalog/home.html'
    context_object_name = 'media_list'
    paginate_by = 12
    
    def get_queryset(self):
        return Media.objects.filter(popularity__gt=0).order_by('-popularity')[:24]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filmes populares
        context['popular_movies'] = Media.objects.filter(
            media_type='movie'
        ).order_by('-popularity')[:6]
        
        # Séries populares
        context['popular_tv_shows'] = Media.objects.filter(
            media_type='tv'
        ).order_by('-popularity')[:6]
        
        # Gêneros para filtros
        context['genres'] = Genre.objects.all()[:10]
        
        # Estatísticas
        context['stats'] = {
            'total_movies': Media.objects.filter(media_type='movie').count(),
            'total_tv_shows': Media.objects.filter(media_type='tv').count(),
            'total_reviews': Review.objects.count(),
        }
        
        return context


class MoviesView(ListView):
    """
    Listagem de filmes
    """
    model = Media
    template_name = 'catalog/movies.html'
    context_object_name = 'movies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Media.objects.filter(media_type='movie')
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(original_title__icontains=search)
            )
        
        # Filtro por gênero
        genre_id = self.request.GET.get('genre')
        if genre_id:
            try:
                genre_id = int(genre_id)
                queryset = queryset.filter(genres__id=genre_id)
            except (ValueError, TypeError):
                pass
        
        # Filtro por ano
        year = self.request.GET.get('year')
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(release_date__year=year)
            except (ValueError, TypeError):
                pass
        
        # Filtro por avaliação mínima
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            try:
                min_rating = int(min_rating)
                queryset = queryset.filter(vote_average__gte=min_rating*2)  # TMDB usa escala 0-10
            except (ValueError, TypeError):
                pass
        
        # Ordenação
        ordering = self.request.GET.get('ordering', '-vote_average')
        valid_orderings = ['-vote_average', '-release_date', 'release_date', 'title', '-title']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-vote_average')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['movies_count'] = self.get_queryset().count()
        
        # Anos disponíveis
        years = Media.objects.filter(
            media_type='movie',
            release_date__isnull=False
        ).dates('release_date', 'year', order='DESC')
        context['years'] = [date.year for date in years]
        
        return context


class TVShowsView(ListView):
    """
    Listagem de séries
    """
    model = Media
    template_name = 'catalog/tv_shows.html'
    context_object_name = 'tv_shows'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Media.objects.filter(media_type='tv')
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(original_title__icontains=search)
            )
        
        # Filtro por gênero
        genre_id = self.request.GET.get('genre')
        if genre_id:
            try:
                genre_id = int(genre_id)
                queryset = queryset.filter(genres__id=genre_id)
            except (ValueError, TypeError):
                pass
        
        # Filtro por ano
        year = self.request.GET.get('year')
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(release_date__year=year)
            except (ValueError, TypeError):
                pass
        
        # Filtro por status (para séries)
        status = self.request.GET.get('status')
        if status and hasattr(queryset.model, 'status'):
            queryset = queryset.filter(status=status)
        
        # Ordenação
        ordering = self.request.GET.get('ordering', '-vote_average')
        valid_orderings = ['-vote_average', '-release_date', 'release_date', 'title', '-title']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-vote_average')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['tv_shows_count'] = self.get_queryset().count()
        
        # Anos disponíveis
        years = Media.objects.filter(
            media_type='tv',
            release_date__isnull=False
        ).dates('release_date', 'year', order='DESC')
        context['years'] = [date.year for date in years]
        
        return context


class SearchView(ListView):
    """
    Busca de filmes e séries
    """
    model = Media
    template_name = 'catalog/search.html'
    context_object_name = 'results'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return Media.objects.none()
            
        queryset = Media.objects.filter(
            Q(title__icontains=query) | 
            Q(original_title__icontains=query) |
            Q(overview__icontains=query)
        )
        
        # Filtro por tipo (filme/série)
        media_type = self.request.GET.get('type')
        if media_type in ['movie', 'tv']:
            queryset = queryset.filter(media_type=media_type)
        
        # Filtro por ano
        year = self.request.GET.get('year')
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(release_date__year=year)
            except (ValueError, TypeError):
                pass
        
        # Ordenação
        ordering = self.request.GET.get('ordering', '-popularity')
        valid_orderings = ['-popularity', '-vote_average', '-release_date', 'title']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-popularity')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class MediaDetailView(DetailView):
    """
    Página de detalhes de um filme/série
    """
    model = Media
    template_name = 'catalog/media_detail.html'
    context_object_name = 'media'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media = self.object
        
        # Avaliações
        reviews = media.reviews.order_by('-created_at')
        context['reviews'] = reviews[:10]
        context['reviews_count'] = reviews.count()
        
        # Avaliação média
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        context['average_rating'] = round(avg_rating, 1) if avg_rating else 0
        
        # Verificar se está nos favoritos do usuário
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, 
                media=media
            ).exists()
            
            # Avaliação do usuário
            try:
                context['user_review'] = Review.objects.get(
                    user=self.request.user,
                    media=media
                )
            except Review.DoesNotExist:
                context['user_review'] = None
        
        # Elenco e equipe
        context['cast'] = media.cast_members.all()[:10]
        context['crew'] = media.crew_members.all()[:5]
        
        # Recomendações (filmes/séries similares)
        similar_media = Media.objects.filter(
            genres__in=media.genres.all(),
            media_type=media.media_type
        ).exclude(id=media.id).distinct()[:6]
        context['similar_media'] = similar_media
        
        return context


class FavoritesView(LoginRequiredMixin, ListView):
    """
    Lista pessoal de favoritos do usuário
    """
    template_name = 'catalog/favorites.html'
    context_object_name = 'favorites'
    paginate_by = 20
    
    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related('media').order_by('-created_at')


class ContentRequestCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário para solicitar novo conteúdo
    """
    model = ContentRequest
    template_name = 'catalog/request_content.html'
    fields = ['title', 'media_type', 'year', 'description']
    success_url = reverse_lazy('catalog:my_requests')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(
            self.request, 
            'Sua solicitação foi enviada com sucesso! Você será notificado quando for processada.'
        )
        return super().form_valid(form)


class MyContentRequestsView(LoginRequiredMixin, ListView):
    """
    Lista de solicitações de conteúdo do usuário
    """
    template_name = 'catalog/my_requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def get_queryset(self):
        return ContentRequest.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class MyReviewsView(LoginRequiredMixin, ListView):
    """
    Lista de avaliações do usuário
    """
    template_name = 'catalog/my_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user
        ).select_related('media').order_by('-created_at')


# Function-based views para AJAX
@login_required
def add_to_favorites(request, media_id):
    """
    Adicionar aos favoritos
    """
    media = get_object_or_404(Media, id=media_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        media=media
    )
    
    if created:
        messages.success(request, f'{media.title} foi adicionado aos seus favoritos!')
    else:
        messages.info(request, f'{media.title} já está nos seus favoritos.')
    
    return redirect('catalog:media_detail', pk=media_id)


@login_required
def remove_from_favorites(request, media_id):
    """
    Remover dos favoritos
    """
    media = get_object_or_404(Media, id=media_id)
    try:
        favorite = Favorite.objects.get(user=request.user, media=media)
        favorite.delete()
        messages.success(request, f'{media.title} foi removido dos seus favoritos.')
    except Favorite.DoesNotExist:
        messages.error(request, 'Item não encontrado nos favoritos.')
    
    return redirect('catalog:media_detail', pk=media_id)


@login_required
def ajax_toggle_favorite(request, media_id):
    """
    Toggle favorito via AJAX
    """
    media = get_object_or_404(Media, id=media_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        media=media
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
        action = 'removed'
    else:
        is_favorite = True
        action = 'added'
    
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'action': action,
        'message': f'{media.title} {"adicionado aos" if is_favorite else "removido dos"} favoritos.'
    })


def ajax_load_more_media(request):
    """
    Carregar mais conteúdo via AJAX (infinite scroll)
    """
    page = request.GET.get('page', 1)
    media_type = request.GET.get('type', 'all')
    
    if media_type == 'all':
        queryset = Media.objects.all()
    else:
        queryset = Media.objects.filter(media_type=media_type)
    
    paginator = Paginator(queryset.order_by('-popularity'), 12)
    
    try:
        media_page = paginator.page(page)
        media_list = []
        
        for media in media_page:
            media_list.append({
                'id': media.id,
                'title': media.title,
                'poster_url': f"https://image.tmdb.org/t/p/w500{media.poster_path}" if media.poster_path else '',
                'media_type': media.get_media_type_display(),
                'release_year': media.release_date.year if media.release_date else None,
                'rating': media.vote_average,
            })
        
        return JsonResponse({
            'success': True,
            'media': media_list,
            'has_next': media_page.has_next(),
            'next_page': media_page.next_page_number() if media_page.has_next() else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
