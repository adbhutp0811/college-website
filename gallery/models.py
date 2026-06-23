from django.db import models
from django.utils import timezone


class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='gallery/albums/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/photos/')
    caption = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = 'Photos'

    def __str__(self):
        return self.title or f"Photo #{self.pk}"
