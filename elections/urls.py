from django.urls import path
from . import views

app_name = 'elections'
urlpatterns = [
    path('', views.ElectionListView.as_view(), name='election_list'),
    path('<int:election_id>/', views.ElectionDetailView.as_view(), name='election_detail'),
    path('<int:election_id>/vote/', views.CastVoteView.as_view(), name='cast_vote'),
    path('<int:election_id>/results/', views.ElectionResultsView.as_view(), name='election_results'),
    path('register-candidacy/', views.RegisterCandidacyView.as_view(), name='register_candidacy'),
    path('my-candidacies/', views.MyCandidaciesView.as_view(), name='my_candidacies'),
    path('manage/', views.ManageElectionsView.as_view(), name='manage_elections'),
    path('manage/create/', views.CreateElectionView.as_view(), name='create_election'),
    path('manage/<int:election_id>/edit/', views.EditElectionView.as_view(), name='edit_election'),
    path('manage/<int:election_id>/delete/', views.DeleteElectionView.as_view(), name='delete_election'),
    path('manage/<int:election_id>/candidates/', views.ManageCandidatesView.as_view(), name='manage_candidates'),
    path('manage/<int:election_id>/candidates/<int:candidate_id>/approve/', views.ApproveCandidateView.as_view(), name='approve_candidate'),
    path('manage/<int:election_id>/candidates/<int:candidate_id>/reject/', views.RejectCandidateView.as_view(), name='reject_candidate'),
]
