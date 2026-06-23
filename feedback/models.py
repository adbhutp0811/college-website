from django.db import models
from django.conf import settings
from students.models import Student
from results.models import Subject
from faculty.models import Faculty


class FeedbackCategory(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Feedback categories'
    
    def __str__(self):
        return self.name


class FeedbackQuestion(models.Model):
    QUESTION_TYPES = [
        ('rating', 'Rating (1-5)'),
        ('text', 'Text Response'),
        ('boolean', 'Yes/No'),
    ]
    
    category = models.ForeignKey(FeedbackCategory, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='rating')
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question_text


class FacultyFeedback(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='faculty_feedbacks')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='feedbacks')
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=9)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'faculty', 'subject', 'semester', 'academic_year')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.student.roll_number} -> {self.faculty.name}'


class FeedbackResponse(models.Model):
    feedback = models.ForeignKey(FacultyFeedback, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE)
    rating_value = models.IntegerField(null=True, blank=True)
    text_value = models.TextField(blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)
    
    class Meta:
        unique_together = ('feedback', 'question')
    
    def __str__(self):
        return f'{self.feedback} - {self.question}'
