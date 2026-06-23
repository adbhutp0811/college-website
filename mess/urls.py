from django.urls import path
from . import views

app_name = 'mess'
urlpatterns = [
    path('', views.MessHomeView.as_view(), name='home'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('fees/', views.MessFeeView.as_view(), name='fees'),
    path('pay/<int:pk>/', views.PayMessFeeView.as_view(), name='pay'),
    path('complaints/', views.ComplaintListView.as_view(), name='complaints'),
    path('complaints/submit/', views.SubmitComplaintView.as_view(), name='submit_complaint'),
    path('staff/complaints/', views.StaffComplaintListView.as_view(), name='staff_complaints'),
    path('staff/complaints/<int:pk>/resolve/', views.ResolveComplaintView.as_view(), name='resolve_complaint'),
]
