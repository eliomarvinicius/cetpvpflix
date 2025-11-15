from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from catalog.models import Media

User = get_user_model()

class Review(models.Model):
    """
    Avaliações e comentários dos usuários
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação de 1 a 5 estrelas"
    )
    comment = models.TextField(blank=True, help_text="Comentário opcional")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.media.title} ({self.rating}⭐)"
    
    class Meta:
        unique_together = ['user', 'media']  # Um usuário só pode avaliar uma vez
        ordering = ['-created_at']

class ReviewLike(models.Model):
    """
    Likes em avaliações
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} liked {self.review.user.username}'s review"
    
    class Meta:
        unique_together = ['user', 'review']
