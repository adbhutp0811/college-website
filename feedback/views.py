from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.utils import timezone
from .models import FeedbackQuestion, FacultyFeedback, FeedbackResponse
from students.models import Student
from results.models import Subject
from faculty.models import Faculty


class GiveFeedbackView(View):
    template_name = 'feedback/give_feedback.html'

    def get(self, request):
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login as student first.')
            return redirect('accounts:student_login')

        student = get_object_or_404(Student, id=student_id)
        current_sem = int(student.student_class.section.replace('Sem ', ''))
        academic_year = student.student_class.academic_year

        faculty_id = request.GET.get('faculty_id')
        subject_id = request.GET.get('subject_id')

        if faculty_id and subject_id:
            existing = FacultyFeedback.objects.filter(
                student=student, faculty_id=faculty_id,
                subject_id=subject_id, semester=current_sem,
                academic_year=academic_year, status='submitted'
            ).exists()
            if existing:
                messages.warning(request, 'You have already submitted feedback for this faculty-subject combination.')
                return redirect('feedback:my_feedback')

        ctx = {
            'student': student,
            'faculties': Faculty.objects.filter(is_active=True),
            'subjects': Subject.objects.filter(student_class=student.student_class),
            'selected_faculty_id': int(faculty_id) if faculty_id else None,
            'selected_subject_id': int(subject_id) if subject_id else None,
        }

        if faculty_id and subject_id:
            ctx['questions'] = FeedbackQuestion.objects.filter(category__is_active=True).select_related('category')

        return render(request, self.template_name, ctx)

    def post(self, request):
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        current_sem = int(student.student_class.section.replace('Sem ', ''))
        academic_year = student.student_class.academic_year

        faculty_id = request.POST.get('faculty_id')
        subject_id = request.POST.get('subject_id')

        feedback, created = FacultyFeedback.objects.get_or_create(
            student=student,
            faculty_id=faculty_id,
            subject_id=subject_id,
            semester=current_sem,
            academic_year=academic_year,
            defaults={'status': 'submitted', 'submitted_at': timezone.now()}
        )

        if not created and feedback.status == 'submitted':
            messages.warning(request, 'Feedback already submitted.')
            return redirect('feedback:my_feedback')

        questions = FeedbackQuestion.objects.filter(category__is_active=True)
        for q in questions:
            if q.question_type == 'rating':
                value = request.POST.get(f'q_{q.id}')
                if value:
                    FeedbackResponse.objects.update_or_create(
                        feedback=feedback, question=q,
                        defaults={'rating_value': int(value)}
                    )
            elif q.question_type == 'text':
                value = request.POST.get(f'q_{q.id}', '')
                FeedbackResponse.objects.update_or_create(
                    feedback=feedback, question=q,
                    defaults={'text_value': value}
                )
            elif q.question_type == 'boolean':
                value = request.POST.get(f'q_{q.id}')
                FeedbackResponse.objects.update_or_create(
                    feedback=feedback, question=q,
                    defaults={'boolean_value': value == 'yes'}
                )

        feedback.status = 'submitted'
        feedback.submitted_at = timezone.now()
        feedback.save()

        messages.success(request, 'Feedback submitted successfully! Thank you for your response.')
        return redirect('feedback:my_feedback')


class MyFeedbackHistoryView(View):
    template_name = 'feedback/my_feedback.html'

    def get(self, request):
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_login')

        student = get_object_or_404(Student, id=student_id)
        feedbacks = FacultyFeedback.objects.filter(student=student).select_related('faculty', 'subject')

        return render(request, self.template_name, {
            'feedbacks': feedbacks,
            'student': student,
        })


class StaffFeedbackResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'feedback/staff_results.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import Avg

        faculty_id = self.request.GET.get('faculty_id')
        if faculty_id:
            feedbacks = FacultyFeedback.objects.filter(
                faculty_id=faculty_id, status='submitted'
            ).select_related('faculty', 'subject')

            results = []
            for fb in feedbacks:
                avg_rating = FeedbackResponse.objects.filter(
                    feedback=fb, question__question_type='rating'
                ).aggregate(avg=Avg('rating_value'))['avg']
                results.append({
                    'feedback': fb,
                    'avg_rating': round(avg_rating, 2) if avg_rating else None,
                    'responses': FeedbackResponse.objects.filter(feedback=fb).select_related('question'),
                })

            ctx['results'] = results
            ctx['selected_faculty'] = get_object_or_404(Faculty, id=faculty_id)

        ctx['faculties'] = Faculty.objects.filter(is_active=True)
        return ctx
