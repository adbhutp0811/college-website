from django.contrib import admin
from .models import MentorAssignment, MentorMeeting, MentorMeetingAttendance, MentorNote

admin.site.register(MentorAssignment)
admin.site.register(MentorMeeting)
admin.site.register(MentorMeetingAttendance)
admin.site.register(MentorNote)
