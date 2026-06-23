from django.db import models
from django.utils import timezone


class Position(models.Model):
    title = models.CharField(max_length=100, unique=True, help_text="e.g., President, Vice President, Secretary")
    description = models.TextField(blank=True)
    max_winners = models.IntegerField(default=1, help_text="Number of winners for this position")
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title


class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    positions = models.ManyToManyField(Position, related_name='elections')
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def has_ended(self):
        return timezone.now() > self.end_date


class Candidate(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='candidacies')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    manifesto = models.TextField(blank=True)
    photo = models.ImageField(upload_to='elections/candidates/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    nomination_date = models.DateTimeField(default=timezone.now)
    vote_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'election', 'position']
        ordering = ['position', 'student']

    def __str__(self):
        return f"{self.student} - {self.position} ({self.election})"


class Vote(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['student', 'election', 'position']
        verbose_name_plural = 'Votes'

    def __str__(self):
        return f"{self.student} voted for {self.candidate} ({self.position})"
