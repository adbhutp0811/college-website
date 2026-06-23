from django.contrib import admin
from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employee_id', 'designation', 'department', 'is_active']
    list_filter = ['designation', 'is_active', 'classes']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    filter_horizontal = ['classes']
