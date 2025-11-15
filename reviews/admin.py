from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewLike

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['media_title', 'user', 'rating', 'created_at', 'likes_count']
    list_filter = ['rating', 'created_at', 'media__media_type']
    search_fields = ['media__title', 'user__username', 'comment']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'likes_count']
    
    fieldsets = (
        ('Avaliação', {
            'fields': ('user', 'media', 'rating', 'comment')
        }),
        ('Informações', {
            'fields': ('created_at', 'updated_at', 'likes_count'),
            'classes': ['collapse']
        })
    )
    
    def media_title(self, obj):
        return obj.media.title
    media_title.short_description = 'Mídia'
    media_title.admin_order_field = 'media__title'
    
    def likes_count(self, obj):
        count = obj.likes.count()
        if count > 0:
            return format_html('<span style="color: green;">{} likes</span>', count)
        return '0 likes'
    likes_count.short_description = 'Likes'

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'review_media', 'review_user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'review__media__title']
    date_hierarchy = 'created_at'
    
    def review_media(self, obj):
        return obj.review.media.title
    review_media.short_description = 'Mídia da Avaliação'
    
    def review_user(self, obj):
        return obj.review.user.username
    review_user.short_description = 'Autor da Avaliação'
