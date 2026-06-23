from django.contrib import admin
from .models import ExamRegistration


@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'academic_year', 'fee_paid', 'status', 'created_at')
    list_filter = ('status', 'semester', 'fee_paid')
    search_fields = ('student__first_name', 'student__roll_number')
