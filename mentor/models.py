from django.db import models
from accounts.models import User
from students.models import Student


class MentorAssignment(models.Model):
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_assignments', limit_choices_to={'role': 'teacher'})
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='mentor')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['faculty', 'student']

    def __str__(self):
        return f'{self.faculty.get_full_name()} -> {self.student.full_name}'


class MentorMeeting(models.Model):
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_meetings')
    meeting_date = models.DateField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-meeting_date']

    def __str__(self):
        return f'{self.faculty.get_full_name()} - {self.meeting_date}'


class MentorMeetingAttendance(models.Model):
    meeting = models.ForeignKey(MentorMeeting, on_delete=models.CASCADE, related_name='attendees')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='meeting_attendance')
    was_present = models.BooleanField(default=True)

    class Meta:
        unique_together = ('meeting', 'student')

    def __str__(self):
        return f'{self.student.full_name} - {self.meeting.meeting_date}'


class MentorNote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentor_notes')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Note on {self.student.full_name} by {self.faculty.get_full_name()}'


class PeerMentor(models.Model):
    mentor = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='peer_mentees')
    mentee = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='peer_mentor')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['mentor', 'mentee']

    def __str__(self):
        return f'{self.mentor.full_name} -> {self.mentee.full_name}'
