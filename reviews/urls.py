from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Criar/editar avaliação
    path('add/<int:media_id>/', views.AddReviewView.as_view(), name='add_review'),
    path('edit/<int:pk>/', views.EditReviewView.as_view(), name='edit_review'),
    path('delete/<int:pk>/', views.DeleteReviewView.as_view(), name='delete_review'),
    
    # AJAX endpoints
    path('ajax/add-review/', views.ajax_add_review, name='ajax_add_review'),
    path('ajax/like-review/<int:review_id>/', views.ajax_like_review, name='ajax_like_review'),
    
    # Lista de avaliações de um filme/série
    path('media/<int:media_id>/', views.MediaReviewsView.as_view(), name='media_reviews'),
]