from django.contrib import admin
from .models import StudyMaterial, Assignment, Submission


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'material_type', 'uploaded_by', 'created_at']
    list_filter = ['material_type', 'subject']
    search_fields = ['title', 'subject__name']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'due_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'subject']
    search_fields = ['title', 'subject__name']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'obtained_marks', 'submitted_at']
    list_filter = ['assignment']
    search_fields = ['student__roll_number']
