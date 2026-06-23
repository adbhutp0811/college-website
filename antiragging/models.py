from django.db import models
from django.core.validators import RegexValidator
from students.models import Student


class AntiRaggingCommittee(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, help_text='e.g., Chairman, Member')
    role = models.CharField(max_length=200, help_text='e.g., Professor, HOD')
    phone = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    email = models.EmailField()
    photo = models.ImageField(upload_to='antiragging/', blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Anti-Ragging Committee Member'
        verbose_name_plural = 'Anti-Ragging Committee'

    def __str__(self):
        return f'{self.name} - {self.role}'


class AntiRaggingUndertaking(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='antiragging_undertaking')
    signed_date = models.DateField(auto_now_add=True)
    uploaded_file = models.FileField(upload_to='antiragging/undertakings/', blank=True, help_text='Upload signed undertaking (PDF/Image)')
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.full_name} - {"Signed" if self.is_accepted else "Pending"}'


class AntiRaggingComplaint(models.Model):
    CATEGORY_CHOICES = [
        ('ragging', 'Ragging Incident'),
        ('harassment', 'Harassment'),
        ('discrimination', 'Discrimination'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='antiragging_complaints', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Anti-Ragging Complaint'
        verbose_name_plural = 'Anti-Ragging Complaints'

    def __str__(self):
        return f'{self.subject} ({self.get_status_display()})'
