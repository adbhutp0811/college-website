from django.urls import path
from . import views

app_name = 'sports'
urlpatterns = [
    path('', views.SportListView.as_view(), name='sport_list'),
    path('<int:pk>/', views.SportDetailView.as_view(), name='sport_detail'),
    path('<int:sport_pk>/teams/create/', views.CreateTeamView.as_view(), name='create_team'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('tournaments/', views.TournamentListView.as_view(), name='tournament_list'),
    path('tournaments/<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
]
