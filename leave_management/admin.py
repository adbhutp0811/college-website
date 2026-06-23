from django.contrib import admin
from .models import LeaveApplication


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'leave_type', 'from_date', 'to_date', 'status', 'applied_at']
    list_filter = ['status', 'leave_type']
    search_fields = ['student__roll_number', 'student__first_name']
