from django.db import models
from students.models import Student
from results.models import Subject


class ExamRegistration(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_registrations')
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=9)
    subjects = models.ManyToManyField(Subject)
    fee_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.roll_number} - Sem {self.semester}'
