from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from .models import Album, Photo


class AlbumListView(ListView):
    model = Album
    template_name = 'gallery/album_list.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.filter(is_published=True)


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'
    pk_url_kwarg = 'album_id'


class ManageAlbumsView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'gallery/manage_albums.html'
    context_object_name = 'albums'
    login_url = 'accounts:login'


class CreateAlbumView(LoginRequiredMixin, CreateView):
    model = Album
    template_name = 'gallery/album_form.html'
    fields = ['title', 'description', 'cover_image', 'is_published']
    success_url = reverse_lazy('gallery:manage_albums')
    login_url = 'accounts:login'

    def form_valid(self, form):
        messages.success(self.request, 'Album created successfully!')
        return super().form_valid(form)


class EditAlbumView(LoginRequiredMixin, UpdateView):
    model = Album
    template_name = 'gallery/album_form.html'
    fields = ['title', 'description', 'cover_image', 'is_published']
    pk_url_kwarg = 'album_id'
    login_url = 'accounts:login'

    def get_success_url(self):
        messages.success(self.request, 'Album updated successfully!')
        return reverse_lazy('gallery:manage_albums')


class DeleteAlbumView(LoginRequiredMixin, DeleteView):
    model = Album
    template_name = 'gallery/delete_confirm.html'
    pk_url_kwarg = 'album_id'
    success_url = reverse_lazy('gallery:manage_albums')
    login_url = 'accounts:login'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['obj_type'] = 'Album'
        ctx['obj_name'] = self.object.title
        ctx['cancel_url'] = reverse_lazy('gallery:manage_albums')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Album deleted successfully!')
        return super().form_valid(form)


class UploadPhotosView(LoginRequiredMixin, TemplateView):
    template_name = 'gallery/upload_photos.html'
    login_url = 'accounts:login'

    def dispatch(self, request, *args, **kwargs):
        self.album = get_object_or_404(Album, pk=kwargs.get('album_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.album
        ctx['photos'] = self.album.photos.all()
        return ctx

    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        if not images:
            messages.error(request, 'Please select at least one photo.')
            return redirect('gallery:upload_photos', album_id=self.album.pk)
        for img in images:
            Photo.objects.create(album=self.album, image=img)
        messages.success(request, f'{len(images)} photo(s) uploaded successfully!')
        return redirect('gallery:upload_photos', album_id=self.album.pk)


class DeletePhotoView(LoginRequiredMixin, View):
    login_url = 'accounts:login'

    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, pk=photo_id)
        album_id = photo.album.pk
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('gallery:upload_photos', album_id=album_id)
