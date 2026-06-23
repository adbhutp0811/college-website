from django.urls import path
from .views import ApplyLeaveView, MyLeavesView, StaffLeaveListView, UpdateLeaveStatusView

app_name = 'leave_management'
urlpatterns = [
    path('apply/', ApplyLeaveView.as_view(), name='apply'),
    path('my-leaves/', MyLeavesView.as_view(), name='my_leaves'),
    path('staff/', StaffLeaveListView.as_view(), name='staff_list'),
    path('update-status/<int:pk>/', UpdateLeaveStatusView.as_view(), name='update_status'),
]
