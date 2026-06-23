from django.urls import path
from .views import (
    StudentAPIView,
    StudentCreateView,
    StudentDeleteView,
    StudentDetailView,
    StudentListView,
    StudentUpdateView,
)
from .id_card import StudentIDCardView

app_name = 'students'

urlpatterns = [
    path('', StudentListView.as_view(), name='list'),
    path('add/', StudentCreateView.as_view(), name='add'),
    path('<int:pk>/', StudentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', StudentUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', StudentDeleteView.as_view(), name='delete'),
    path('<int:pk>/id-card/', StudentIDCardView.as_view(), name='id_card'),
    path('api/students/', StudentAPIView.as_view(), name='api_students'),
]
