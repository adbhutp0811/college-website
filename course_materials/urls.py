from django.urls import path
from .views import (
    MaterialListView, MaterialCreateView,
    AssignmentListView, AssignmentCreateView, AssignmentUpdateView,
    SubmitAssignmentView, MySubmissionsView,
    StaffSubmissionsView, GradeSubmissionView,
    AssignmentDeleteView
)

app_name = 'course_materials'
urlpatterns = [
    path('materials/', MaterialListView.as_view(), name='material_list'),
    path('materials/create/', MaterialCreateView.as_view(), name='create_material'),
    path('assignments/', AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/create/', AssignmentCreateView.as_view(), name='create_assignment'),
    path('assignments/<int:pk>/edit/', AssignmentUpdateView.as_view(), name='edit_assignment'),
    path('assignments/<int:pk>/submit/', SubmitAssignmentView.as_view(), name='submit_assignment'),
    path('submissions/', MySubmissionsView.as_view(), name='my_submissions'),
    path('assignments/<int:pk>/submissions/', StaffSubmissionsView.as_view(), name='staff_submissions'),
    path('grade/<int:pk>/', GradeSubmissionView.as_view(), name='grade_submission'),
    path('assignments/<int:pk>/delete/', AssignmentDeleteView.as_view(), name='delete_assignment'),
]
