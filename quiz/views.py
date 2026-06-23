import json
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from results.models import Subject
from students.models import Student
from .models import Answer, Question, Quiz, QuizAttempt


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.session.get('student_id') is not None


class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz/quiz_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        if self.request.session.get('student_id'):
            student = get_object_or_404(Student, pk=self.request.session['student_id'])
            return Quiz.objects.filter(is_published=True, subject__student_class=student.student_class)
        return Quiz.objects.filter(is_published=True)


class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'


class StartQuizView(StudentRequiredMixin, View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        if not quiz.is_active:
            messages.error(request, 'This quiz is not available right now.')
            return redirect('quiz:quiz_list')
        attempt, created = QuizAttempt.objects.get_or_create(student_id=request.session['student_id'], quiz=quiz)
        if not created:
            messages.warning(request, 'You have already attempted this quiz.')
            return redirect('quiz:quiz_result', pk=pk)
        return render(request, 'quiz/take_quiz.html', {'quiz': quiz})


class SubmitQuizView(StudentRequiredMixin, View):
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        attempt = get_object_or_404(QuizAttempt, quiz=quiz, student_id=request.session['student_id'])
        if attempt.completed_at:
            messages.error(request, 'Quiz already submitted.')
            return redirect('quiz:quiz_result', pk=pk)
        score = 0
        total = 0
        for question in quiz.questions.all():
            selected = request.POST.get(f'q_{question.id}', '')
            is_correct = selected == question.correct_answer
            if is_correct:
                score += question.marks
            total += question.marks
            Answer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={'selected_answer': selected, 'is_correct': is_correct},
            )
        attempt.score = score
        attempt.total_marks = total
        attempt.completed_at = timezone.now()
        attempt.save()
        messages.success(request, f'Quiz submitted! You scored {score}/{total}.')
        return redirect('quiz:quiz_result', pk=pk)


class QuizResultView(StudentRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quiz/quiz_result.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt = get_object_or_404(QuizAttempt, quiz=self.get_object(), student_id=self.request.session['student_id'])
        ctx['attempt'] = attempt
        ctx['answers'] = Answer.objects.filter(attempt=attempt).select_related('question')
        return ctx


class CreateQuizView(StaffRequiredMixin, View):
    template_name = 'quiz/create_quiz.html'

    def get(self, request):
        subjects = Subject.objects.all()
        return render(request, self.template_name, {'subjects': subjects})

    def post(self, request):
        subject = get_object_or_404(Subject, pk=request.POST.get('subject'))
        quiz = Quiz.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            subject=subject,
            duration_minutes=request.POST.get('duration_minutes'),
            total_marks=request.POST.get('total_marks'),
            pass_marks=request.POST.get('pass_marks', 0),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
        )
        messages.success(request, 'Quiz created. Now add questions.')
        return redirect('quiz:add_questions', pk=quiz.pk)


class AddQuestionsView(StaffRequiredMixin, View):
    template_name = 'quiz/add_questions.html'

    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        questions = Question.objects.filter(quiz=quiz)
        return render(request, self.template_name, {'quiz': quiz, 'questions': questions})

    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        text = request.POST.get('text', '').strip()
        if text:
            Question.objects.create(
                quiz=quiz,
                text=text,
                option_a=request.POST.get('option_a', ''),
                option_b=request.POST.get('option_b', ''),
                option_c=request.POST.get('option_c', ''),
                option_d=request.POST.get('option_d', ''),
                correct_answer=request.POST.get('correct_answer', 'A'),
                marks=request.POST.get('marks', 1),
            )
            messages.success(request, 'Question added.')
        return redirect('quiz:add_questions', pk=pk)


class MyResultsView(StudentRequiredMixin, ListView):
    template_name = 'quiz/my_results.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        return QuizAttempt.objects.filter(student_id=self.request.session['student_id']).select_related('quiz').order_by('-completed_at')
