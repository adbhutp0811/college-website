from django.urls import path
from .views import TimetableView, ManageTimetableView, AddSlotView, DeleteSlotView

app_name = 'timetable'
urlpatterns = [
    path('', TimetableView.as_view(), name='timetable'),
    path('manage/', ManageTimetableView.as_view(), name='manage'),
    path('add-slot/', AddSlotView.as_view(), name='add_slot'),
    path('delete-slot/<int:pk>/', DeleteSlotView.as_view(), name='delete_slot'),
]
