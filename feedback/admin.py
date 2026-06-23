from django.contrib import admin
from .models import FeedbackCategory, FeedbackQuestion, FacultyFeedback, FeedbackResponse


@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']


@admin.register(FeedbackQuestion)
class FeedbackQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'category', 'question_type', 'is_required', 'order']
    list_filter = ['category', 'question_type']
    ordering = ['category', 'order']


@admin.register(FacultyFeedback)
class FacultyFeedbackAdmin(admin.ModelAdmin):
    list_display = ['student', 'faculty', 'subject', 'semester', 'status', 'submitted_at']
    list_filter = ['status', 'semester']


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['feedback', 'question', 'rating_value']
