from django.urls import path
from . import views

app_name = 'mentor'
urlpatterns = [
    path('', views.MentorDashboardView.as_view(), name='dashboard'),
    path('my-mentees/', views.MyMenteesView.as_view(), name='my_mentees'),
    path('mentee/<int:pk>/', views.MenteeDetailView.as_view(), name='mentee_detail'),
    path('mentee/<int:pk>/add-note/', views.AddMentorNoteView.as_view(), name='add_note'),
    path('meetings/', views.MeetingListView.as_view(), name='meetings'),
    path('meetings/create/', views.CreateMeetingView.as_view(), name='create_meeting'),
    path('assign/', views.AssignMentorView.as_view(), name='assign'),
    path('student/', views.StudentMentorView.as_view(), name='student_mentor'),
]
