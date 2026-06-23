from django.urls import path
from . import views

app_name = 'quiz'
urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:pk>/start/', views.StartQuizView.as_view(), name='start_quiz'),
    path('<int:pk>/submit/', views.SubmitQuizView.as_view(), name='submit_quiz'),
    path('<int:pk>/result/', views.QuizResultView.as_view(), name='quiz_result'),
    path('create/', views.CreateQuizView.as_view(), name='create_quiz'),
    path('<int:pk>/add-questions/', views.AddQuestionsView.as_view(), name='add_questions'),
    path('my-results/', views.MyResultsView.as_view(), name='my_results'),
]
