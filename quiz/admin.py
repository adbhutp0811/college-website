from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, Answer

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAttempt)
admin.site.register(Answer)
