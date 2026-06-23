from django.db import models
from django.utils import timezone


class Alumni(models.Model):
    BATCH_YEARS = [(str(y), str(y)) for y in range(2000, 2031)]

    student = models.ForeignKey('students.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='alumni_profiles')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    graduation_year = models.CharField(max_length=4, choices=BATCH_YEARS)
    program = models.CharField(max_length=100)
    current_occupation = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    photo = models.ImageField(upload_to='alumni/photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    registered_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-graduation_year', 'last_name']
        verbose_name_plural = 'Alumni'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.graduation_year})"


class AlumniEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=300, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    registration_deadline = models.DateField(blank=True, null=True)
    max_participants = models.IntegerField(default=0, help_text="0 = unlimited")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(AlumniEvent, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(default=timezone.now)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ['alumni', 'event']

    def __str__(self):
        return f"{self.alumni} -> {self.event}"


class Donation(models.Model):
    alumni = models.ForeignKey(Alumni, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donor_name = models.CharField(max_length=200)
    donor_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=200, blank=True)
    transaction_id = models.CharField(max_length=200, unique=True)
    payment_method = models.CharField(max_length=50, default='online')
    notes = models.TextField(blank=True)
    donated_at = models.DateTimeField(default=timezone.now)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ['-donated_at']

    def __str__(self):
        return f"{self.donor_name} - ${self.amount}"
