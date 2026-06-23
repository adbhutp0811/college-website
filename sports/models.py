from django.db import models
from students.models import Student


class Sport(models.Model):
    CATEGORY_CHOICES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
    ]
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Team(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Student, related_name='sports_teams')
    coach_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sport', 'name']

    def __str__(self):
        return f'{self.sport.name} - {self.name}'


class Tournament(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='tournaments')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} ({self.sport.name})'


class Achievement(models.Model):
    MEDAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
        ('participation', 'Participation'),
        ('other', 'Other'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sports_achievements')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='achievements')
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True, related_name='achievements')
    title = models.CharField(max_length=200)
    medal = models.CharField(max_length=20, choices=MEDAL_CHOICES, default='participation')
    achievement_date = models.DateField()
    description = models.TextField(blank=True)
    certificate = models.FileField(upload_to='sports/certificates/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-achievement_date']

    def __str__(self):
        return f'{self.student.full_name} - {self.title}'
