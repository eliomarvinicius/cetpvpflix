from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Página principal
    path('', views.HomeView.as_view(), name='home'),
    
    # Listagens
    path('movies/', views.MoviesView.as_view(), name='movies'),
    path('tv-shows/', views.TVShowsView.as_view(), name='tv_shows'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Detalhes
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='media_detail'),
    
    # Favoritos
    path('my-list/', views.FavoritesView.as_view(), name='favorites'),
    path('add-favorite/<int:media_id>/', views.add_to_favorites, name='add_favorite'),
    path('remove-favorite/<int:media_id>/', views.remove_from_favorites, name='remove_favorite'),
    
    # Solicitações de conteúdo
    path('request-content/', views.ContentRequestCreateView.as_view(), name='request_content'),
    path('my-requests/', views.MyContentRequestsView.as_view(), name='my_requests'),
    
    # Avaliações do usuário
    path('my-reviews/', views.MyReviewsView.as_view(), name='my_reviews'),
    
    # AJAX endpoints
    path('ajax/toggle-favorite/<int:media_id>/', views.ajax_toggle_favorite, name='ajax_toggle_favorite'),
    path('ajax/load-more-media/', views.ajax_load_more_media, name='ajax_load_more_media'),
]