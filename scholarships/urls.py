from django.urls import path
from . import views

app_name = 'scholarships'
urlpatterns = [
    path('', views.SchemeListView.as_view(), name='scheme_list'),
    path('<int:pk>/', views.SchemeDetailView.as_view(), name='scheme_detail'),
    path('<int:pk>/apply/', views.ApplyScholarshipView.as_view(), name='apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my_applications'),
    path('staff/', views.StaffApplicationListView.as_view(), name='staff_list'),
    path('staff/<int:pk>/review/', views.ReviewApplicationView.as_view(), name='review'),
]
