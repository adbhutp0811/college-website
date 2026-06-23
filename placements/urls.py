from django.urls import path
from .views import CompanyListView, PlacementDriveListView, PlacementDriveDetailView, ApplyDriveView, MyApplicationsView, StaffApplicationsView, UpdateApplicationStatusView

app_name = 'placements'
urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('drives/', PlacementDriveListView.as_view(), name='drive_list'),
    path('drives/<int:pk>/', PlacementDriveDetailView.as_view(), name='drive_detail'),
    path('drives/<int:pk>/apply/', ApplyDriveView.as_view(), name='apply_drive'),
    path('my-applications/', MyApplicationsView.as_view(), name='my_applications'),
    path('staff-applications/', StaffApplicationsView.as_view(), name='staff_applications'),
    path('update-status/<int:pk>/', UpdateApplicationStatusView.as_view(), name='update_status'),
]
