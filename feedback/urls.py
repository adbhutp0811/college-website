from django.urls import path
from .views import GiveFeedbackView, MyFeedbackHistoryView, StaffFeedbackResultsView

app_name = 'feedback'
urlpatterns = [
    path('give/', GiveFeedbackView.as_view(), name='give_feedback'),
    path('my-feedback/', MyFeedbackHistoryView.as_view(), name='my_feedback'),
    path('staff-results/', StaffFeedbackResultsView.as_view(), name='staff_results'),
]
