from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from .models import Event


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        qs = Event.objects.all()
        cat = self.request.GET.get('category')
        if cat:
            qs = qs.filter(category=cat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Event.CATEGORY_CHOICES
        ctx['current_category'] = self.request.GET.get('category', '')
        return ctx


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    slug_field = 'pk'


class CreateEventView(LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['title', 'description', 'date', 'end_date', 'venue', 'category', 'registration_link']
    success_url = reverse_lazy('events:event_list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)
