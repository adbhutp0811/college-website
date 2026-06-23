from django.urls import path
from . import views

app_name = 'exam_seating'
urlpatterns = [
    path('', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedule/<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedule/create/', views.CreateScheduleView.as_view(), name='create_schedule'),
    path('schedule/<int:pk>/allocate/', views.AllocateSeatsView.as_view(), name='allocate_seats'),
    path('my-seating/', views.StudentSeatingView.as_view(), name='student_seating'),
]
