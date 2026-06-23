from django.urls import path
from .views import GrievanceCreateView, GrievanceListView, StaffGrievanceListView, GrievanceResolveView

app_name = 'grievances'
urlpatterns = [
    path('', GrievanceListView.as_view(), name='list'),
    path('submit/', GrievanceCreateView.as_view(), name='submit'),
    path('staff/', StaffGrievanceListView.as_view(), name='staff_list'),
    path('<int:pk>/resolve/', GrievanceResolveView.as_view(), name='resolve'),
]
