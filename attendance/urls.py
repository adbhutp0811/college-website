from django.urls import path
from .views import (
    AttendanceHistoryView,
    AttendanceSummaryView,
    GetStudentsForClassView,
    MarkAttendanceView,
    SaveAttendanceView,
    AttendanceNotifyView,
    AttendanceSMSView,
    CustomSMSView,
    CustomEmailView,
)

app_name = 'attendance'

urlpatterns = [
    path('mark/', MarkAttendanceView.as_view(), name='mark'),
    path('api/get-students/<int:class_id>/', GetStudentsForClassView.as_view(), name='get_students'),
    path('api/save/', SaveAttendanceView.as_view(), name='save'),
    path('history/', AttendanceHistoryView.as_view(), name='history'),
    path('summary/', AttendanceSummaryView.as_view(), name='summary'),
    path('notify/', AttendanceNotifyView.as_view(), name='notify'),
    path('sms/', AttendanceSMSView.as_view(), name='sms'),
    path('custom-sms/', CustomSMSView.as_view(), name='custom_sms'),
    path('custom-email/', CustomEmailView.as_view(), name='custom_email'),
]
