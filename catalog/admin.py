from django.contrib import admin
from django.utils.html import format_html
from .models import Media, Genre, Cast, Crew, Favorite, ContentRequest

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id']
    search_fields = ['name']
    list_filter = ['name']
    ordering = ['name']

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'release_date', 'vote_average', 'poster_preview']
    list_filter = ['media_type', 'release_date', 'genres']
    search_fields = ['title', 'original_title', 'overview']
    readonly_fields = ['tmdb_id', 'poster_preview', 'backdrop_preview']
    filter_horizontal = ['genres']
    date_hierarchy = 'release_date'
    list_per_page = 25
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'original_title', 'media_type', 'overview')
        }),
        ('TMDB Data', {
            'fields': ('tmdb_id', 'poster_path', 'poster_preview', 'backdrop_path', 'backdrop_preview'),
            'classes': ['collapse']
        }),
        ('Detalhes', {
            'fields': ('release_date', 'runtime', 'vote_average', 'vote_count', 'popularity')
        }),
        ('Série (se aplicável)', {
            'fields': ('number_of_seasons', 'number_of_episodes'),
            'classes': ['collapse']
        }),
        ('Relacionamentos', {
            'fields': ('genres',)
        }),
        ('Outros', {
            'fields': ('original_language',),
            'classes': ['collapse']
        })
    )
    
    def poster_preview(self, obj):
        if obj.poster_path:
            return format_html(
                '<img src="https://image.tmdb.org/t/p/w200{}" style="max-height: 200px;"/>',
                obj.poster_path
            )
        return "Sem poster"
    poster_preview.short_description = "Preview do Poster"
    
    def backdrop_preview(self, obj):
        if obj.backdrop_path:
            return format_html(
                '<img src="https://image.tmdb.org/t/p/w500{}" style="max-width: 300px;"/>',
                obj.backdrop_path
            )
        return "Sem backdrop"
    backdrop_preview.short_description = "Preview do Backdrop"

@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ['name', 'character', 'media', 'order']
    search_fields = ['name', 'character', 'media__title']
    list_filter = ['media__media_type']
    ordering = ['media', 'order']

@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ['name', 'job', 'department', 'media']
    search_fields = ['name', 'job', 'department', 'media__title']
    list_filter = ['job', 'department', 'media__media_type']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'media', 'created_at']
    list_filter = ['created_at', 'media__media_type']
    search_fields = ['user__username', 'media__title']
    date_hierarchy = 'created_at'

@admin.register(ContentRequest)
class ContentRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'user', 'status', 'created_at']
    list_filter = ['status', 'media_type', 'created_at']
    search_fields = ['title', 'user__username', 'description']
    date_hierarchy = 'created_at'
    actions = ['approve_requests', 'reject_requests']
    
    fieldsets = (
        ('Solicitação', {
            'fields': ('user', 'title', 'media_type', 'year', 'description')
        }),
        ('Administração', {
            'fields': ('status', 'admin_notes')
        }),
    )
    
    def approve_requests(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} solicitações foram aprovadas.')
    approve_requests.short_description = "Aprovar solicitações selecionadas"
    
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} solicitações foram rejeitadas.')
    reject_requests.short_description = "Rejeitar solicitações selecionadas"
