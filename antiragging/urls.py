from django.urls import path
from . import views

app_name = 'antiragging'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('committee/', views.CommitteeView.as_view(), name='committee'),
    path('undertaking/', views.UndertakingView.as_view(), name='undertaking'),
    path('undertaking/sign/', views.SignUndertakingView.as_view(), name='sign_undertaking'),
    path('complaint/submit/', views.SubmitComplaintView.as_view(), name='submit_complaint'),
    path('complaints/', views.ComplaintListView.as_view(), name='complaint_list'),
    path('staff/complaints/', views.StaffComplaintListView.as_view(), name='staff_complaints'),
    path('staff/complaints/<int:pk>/resolve/', views.ResolveComplaintView.as_view(), name='resolve_complaint'),
]
