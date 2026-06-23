from django.urls import path
from .views import HostelListView, HostelDetailView, ApplyRoomView, MyAllocationView, StaffAllocationsView, DeallocateRoomView

app_name = 'hostel'
urlpatterns = [
    path('', HostelListView.as_view(), name='hostel_list'),
    path('<int:pk>/', HostelDetailView.as_view(), name='hostel_detail'),
    path('room/<int:pk>/apply/', ApplyRoomView.as_view(), name='apply_room'),
    path('my-allocation/', MyAllocationView.as_view(), name='my_allocation'),
    path('staff-allocations/', StaffAllocationsView.as_view(), name='staff_allocations'),
    path('deallocate/<int:pk>/', DeallocateRoomView.as_view(), name='deallocate_room'),
]
