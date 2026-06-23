from django.db import models
from django.conf import settings
from students.models import Student, Class
from results.models import Subject


class StudyMaterial(models.Model):
    MATERIAL_TYPES = [
        ('notes', 'Class Notes'),
        ('presentation', 'Presentation'),
        ('reference', 'Reference Material'),
        ('question_bank', 'Question Bank'),
        ('lab_manual', 'Lab Manual'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_materials')
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='study_materials')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='notes')
    file = models.FileField(upload_to='study_materials/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.subject.name}'


class Assignment(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    max_marks = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.title} - {self.subject.name}'

    @property
    def is_past_due(self):
        from django.utils import timezone
        return timezone.now() > self.due_date


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignment_submissions')
    file = models.FileField(upload_to='submissions/')
    remarks = models.TextField(blank=True)
    obtained_marks = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.roll_number} - {self.assignment.title}'
