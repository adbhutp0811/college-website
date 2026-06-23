from django.db import models
from django.utils import timezone
from students.models import Student
from results.models import Subject


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    duration_minutes = models.IntegerField(help_text='Duration in minutes')
    total_marks = models.IntegerField()
    pass_marks = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return self.is_published and self.start_time <= now <= self.end_time

    @property
    def has_ended(self):
        return timezone.now() > self.end_time

    @property
    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    marks = models.IntegerField(default=1)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.quiz.title} - Q{self.id}'


class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f'{self.student.full_name} - {self.quiz.title}'

    @property
    def percentage(self):
        if self.total_marks:
            return round((self.score / self.total_marks) * 100, 2)
        return 0

    @property
    def is_passed(self):
        return self.score >= self.quiz.pass_marks


class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    selected_answer = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f'{self.attempt.student.full_name} - Q{self.question.id}'
