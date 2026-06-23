from django.urls import path
from .views import ExamFormCreateView, ExamFormListView, StaffExamFormListView, ExamFormApproveView

app_name = 'exam_forms'
urlpatterns = [
    path('', ExamFormListView.as_view(), name='list'),
    path('submit/', ExamFormCreateView.as_view(), name='submit'),
    path('staff/', StaffExamFormListView.as_view(), name='staff_list'),
    path('<int:pk>/approve/', ExamFormApproveView.as_view(), name='approve'),
]
