from django.contrib import admin
from .models import Grievance


@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('subject', 'student', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('subject', 'description', 'student__first_name', 'student__roll_number')
