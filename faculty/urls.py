from django.urls import path
from .views import FacultyListView, FacultyCreateView, FacultyUpdateView, FacultyDeleteView

app_name = 'faculty'

urlpatterns = [
    path('', FacultyListView.as_view(), name='list'),
    path('add/', FacultyCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', FacultyUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', FacultyDeleteView.as_view(), name='delete'),
]
