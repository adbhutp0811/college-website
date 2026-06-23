from django.db import models
from students.models import Student


class ScholarshipScheme(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    eligibility_criteria = models.TextField(help_text='Eligibility requirements')
    application_deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-application_deadline']

    def __str__(self):
        return self.name


class ScholarshipApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarship_applications')
    scheme = models.ForeignKey(ScholarshipScheme, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    documents = models.FileField(upload_to='scholarships/documents/', blank=True, help_text='Upload supporting documents')
    remarks = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('student', 'scheme')

    def __str__(self):
        return f'{self.student.full_name} - {self.scheme.name}'
