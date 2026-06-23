from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.AlbumListView.as_view(), name='album_list'),
    path('<int:album_id>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('manage/', views.ManageAlbumsView.as_view(), name='manage_albums'),
    path('manage/create/', views.CreateAlbumView.as_view(), name='create_album'),
    path('manage/<int:album_id>/edit/', views.EditAlbumView.as_view(), name='edit_album'),
    path('manage/<int:album_id>/delete/', views.DeleteAlbumView.as_view(), name='delete_album'),
    path('manage/<int:album_id>/upload/', views.UploadPhotosView.as_view(), name='upload_photos'),
    path('manage/photo/<int:photo_id>/delete/', views.DeletePhotoView.as_view(), name='delete_photo'),
]
