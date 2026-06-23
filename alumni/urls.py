from django.urls import path
from .views import (
    AlumniDirectoryView, AlumniRegistrationView, RegistrationSuccessView,
    AlumniProfileView, AlumniEventListView, AlumniEventDetailView,
    RegisterForEventView, DonationView, DonationSuccessView,
    ManageAlumniView, VerifyAlumniView, DeleteAlumniView,
    ManageEventsView, CreateEventView, EditEventView, DeleteEventView,
    DonationListView,
)

app_name = 'alumni'
urlpatterns = [
    path('', AlumniDirectoryView.as_view(), name='directory'),
    path('register/', AlumniRegistrationView.as_view(), name='register'),
    path('register/success/', RegistrationSuccessView.as_view(), name='registration_success'),
    path('my-profile/', AlumniProfileView.as_view(), name='my_profile'),
    path('events/', AlumniEventListView.as_view(), name='event_list'),
    path('events/<int:event_id>/', AlumniEventDetailView.as_view(), name='event_detail'),
    path('events/<int:event_id>/register/', RegisterForEventView.as_view(), name='register_for_event'),
    path('donate/', DonationView.as_view(), name='donate'),
    path('donate/success/', DonationSuccessView.as_view(), name='donation_success'),
    path('manage/', ManageAlumniView.as_view(), name='manage'),
    path('manage/<int:pk>/verify/', VerifyAlumniView.as_view(), name='verify'),
    path('manage/<int:pk>/delete/', DeleteAlumniView.as_view(), name='delete'),
    path('manage/events/', ManageEventsView.as_view(), name='manage_events'),
    path('manage/events/create/', CreateEventView.as_view(), name='create_event'),
    path('manage/events/<int:event_id>/edit/', EditEventView.as_view(), name='edit_event'),
    path('manage/events/<int:event_id>/delete/', DeleteEventView.as_view(), name='delete_event'),
    path('manage/donations/', DonationListView.as_view(), name='donation_list'),
]
