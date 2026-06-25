from django.contrib import admin
from .models import MentorAssignment, MentorMeeting, MentorMeetingAttendance, MentorNote, PeerMentor


@admin.register(MentorAssignment)
class MentorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['faculty', 'student', 'is_active', 'assigned_at']
    list_filter = ['is_active', 'faculty']
    search_fields = ['faculty__first_name', 'faculty__last_name', 'student__first_name', 'student__last_name', 'student__roll_number']
    list_editable = ['is_active']
    autocomplete_fields = ['faculty', 'student']


admin.site.register(MentorMeeting)
admin.site.register(MentorMeetingAttendance)
admin.site.register(MentorNote)
admin.site.register(PeerMentor)
