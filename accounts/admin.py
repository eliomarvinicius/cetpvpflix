from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'favorites_count']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    date_hierarchy = 'date_joined'
    
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil', {
            'fields': ('bio', 'birth_date', 'avatar', 'avatar_preview')
        }),
        ('Estatísticas', {
            'fields': ('favorites_count', 'reviews_count'),
            'classes': ['collapse']
        }),
    )
    readonly_fields = ['date_joined', 'last_login', 'favorites_count', 'reviews_count', 'avatar_preview']
    
    def favorites_count(self, obj):
        count = obj.favorite_set.count() if hasattr(obj, 'favorite_set') else 0
        return f'{count} favorito{"s" if count != 1 else ""}'
    favorites_count.short_description = 'Favoritos'
    
    def reviews_count(self, obj):
        count = obj.review_set.count() if hasattr(obj, 'review_set') else 0
        return f'{count} avaliação{"ões" if count != 1 else ""}'
    reviews_count.short_description = 'Avaliações'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;"/>',
                obj.avatar.url
            )
        return "Sem avatar"
    avatar_preview.short_description = "Preview do Avatar"
