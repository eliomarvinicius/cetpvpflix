from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Genre(models.Model):
    """
    Gêneros de filmes e séries
    """
    name = models.CharField(max_length=100, unique=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Media(models.Model):
    """
    Modelo base para filmes e séries
    """
    MEDIA_TYPES = [
        ('movie', 'Filme'),
        ('tv', 'Série'),
    ]
    
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    overview = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=200, blank=True)
    backdrop_path = models.CharField(max_length=200, blank=True)
    tmdb_id = models.IntegerField(unique=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    runtime = models.IntegerField(null=True, blank=True, help_text="Duração em minutos")
    genres = models.ManyToManyField(Genre, blank=True)
    vote_average = models.FloatField(default=0.0)  # Avaliação do TMDB
    vote_count = models.IntegerField(default=0)    # Número de votos do TMDB
    popularity = models.FloatField(default=0.0)
    original_language = models.CharField(max_length=10, blank=True)
    
    # Campos para séries
    number_of_seasons = models.IntegerField(null=True, blank=True)
    number_of_episodes = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"
    
    class Meta:
        ordering = ['-popularity', '-release_date']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['-popularity']),
        ]

class Cast(models.Model):
    """
    Elenco dos filmes/séries
    """
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='cast_members')
    name = models.CharField(max_length=200)
    character = models.CharField(max_length=200, blank=True, null=True)
    profile_path = models.CharField(max_length=200, blank=True, null=True)
    tmdb_person_id = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} as {self.character}"
    
    class Meta:
        ordering = ['order']

class Crew(models.Model):
    """
    Equipe técnica dos filmes/séries
    """
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='crew_members')
    name = models.CharField(max_length=200)
    job = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    profile_path = models.CharField(max_length=200, blank=True, null=True)
    tmdb_person_id = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.job}"

class Favorite(models.Model):
    """
    Lista de favoritos do usuário
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.media.title}"
    
    class Meta:
        unique_together = ['user', 'media']
        ordering = ['-created_at']

class ContentRequest(models.Model):
    """
    Solicitações de conteúdo pelos usuários
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovada'),
        ('rejected', 'Rejeitada'),
        ('added', 'Adicionada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_requests')
    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=10, choices=Media.MEDIA_TYPES)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField(help_text="Por que você gostaria que este conteúdo fosse adicionado?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Notas do administrador")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-created_at']
