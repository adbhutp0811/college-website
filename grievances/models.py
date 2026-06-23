from django.db import models
from students.models import Student


class Grievance(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'), ('harassment', 'Harassment'),
        ('faculty', 'Faculty Related'), ('facility', 'Facility Issue'),
        ('exam', 'Exam Related'), ('fee', 'Fee Related'),
        ('hostel', 'Hostel Issue'), ('other', 'Other'),
    ]
    STATUS_CHOICES = [('pending', 'Pending'), ('reviewing', 'Reviewing'), ('resolved', 'Resolved'), ('rejected', 'Rejected')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grievances')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.full_name} - {self.subject[:50]}'
