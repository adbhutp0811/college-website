from django.urls import path
from .views import EventListView, EventDetailView, CreateEventView

app_name = 'events'
urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('create/', CreateEventView.as_view(), name='create_event'),
]
