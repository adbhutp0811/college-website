from django.contrib import admin
from .models import Album, Photo


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'photo_count', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']

    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'is_featured', 'uploaded_at']
    list_filter = ['is_featured', 'album', 'uploaded_at']
    search_fields = ['title', 'caption']
