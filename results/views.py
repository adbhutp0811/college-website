from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.db.models import Avg, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView
from students.models import Class, Student
from xhtml2pdf import pisa
from .forms import BulkResultForm, ResultForm
from .models import Exam, Result, Subject, calculate_sgpa


def render_to_pdf(template_src, context_dict):
    html = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
    if pdf.err:
        return None
    return result.getvalue()


class ManageResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'results/manage_results.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        ctx['exam_form'] = ResultForm()
        return ctx


class GetSubjectsExamView(LoginRequiredMixin, View):
    def get(self, request):
        class_id = request.GET.get('class_id')
        exam_id = request.GET.get('exam_id')
        subject_id = request.GET.get('subject_id')
        subjects = Subject.objects.filter(student_class_id=class_id).values('id', 'name', 'max_marks')
        exams = Exam.objects.filter(student_class_id=class_id).values('id', 'name', 'exam_type')
        data = {
            'subjects': list(subjects),
            'exams': list(exams),
        }
        if exam_id and subject_id:
            results = Result.objects.filter(
                exam_id=exam_id, subject_id=subject_id
            ).values('student_id', 'marks_obtained', 'grade', 'grade_auto')
            data['results'] = list(results)
        return JsonResponse(data)


class SaveResultsView(LoginRequiredMixin, View):
    def post(self, request):
        exam_id = request.POST.get('exam')
        subject_id = request.POST.get('subject')
        marks_data = {k: v for k, v in request.POST.items() if k.startswith('marks_')}
        grade_data = {k: v for k, v in request.POST.items() if k.startswith('grade_')}
        grade_auto_data = {k: v for k, v in request.POST.items() if k.startswith('grade_auto_')}
        subject = get_object_or_404(Subject, id=subject_id)
        for key, value in marks_data.items():
            if value:
                student_id = int(key.replace('marks_', ''))
                grade = grade_data.get(f'grade_{student_id}', '')
                grade_auto = grade_auto_data.get(f'grade_auto_{student_id}', 'true') == 'true'
                defaults = {
                    'marks_obtained': float(value),
                    'grade': grade,
                    'grade_auto': grade_auto,
                }
                result, created = Result.objects.get_or_create(
                    student_id=student_id,
                    exam_id=exam_id,
                    subject_id=subject_id,
                    defaults=defaults,
                )
                if not created:
                    result.marks_obtained = float(value)
                    result.grade = grade
                    result.grade_auto = grade_auto
                    result.save()
        messages.success(request, 'Results saved successfully!')
        return redirect('results:manage')


class ClassResultSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'results/class_summary.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        class_id = self.request.GET.get('class', '')
        exam_id = self.request.GET.get('exam', '')
        ctx['classes'] = Class.objects.all()
        ctx['exams'] = Exam.objects.all()
        ctx['current_class'] = class_id
        ctx['current_exam'] = exam_id

        if class_id and exam_id:
            students = Student.objects.filter(student_class_id=class_id, is_deleted=False)
            subjects = Subject.objects.filter(student_class_id=class_id)
            summary = []
            for s in students:
                results = Result.objects.filter(student=s, exam_id=exam_id)
                total_marks = sum(r.total_marks for r in results)
                max_marks = sum(r.subject.max_marks for r in results)
                sgpa, total_credits = calculate_sgpa(results)
                failed = any(not r.is_pass for r in results)
                grade = self.sgpa_to_grade(sgpa)
                summary.append({
                    'student': s,
                    'results': results,
                    'total_marks': round(total_marks, 2),
                    'max_marks': max_marks,
                    'sgpa': sgpa,
                    'total_credits': total_credits,
                    'grade': grade,
                    'failed': failed,
                })
            summary.sort(key=lambda x: x['sgpa'], reverse=True)
            ctx['summary'] = summary
            ctx['subjects'] = subjects
            ctx['passed'] = sum(1 for s in summary if not s['failed'])
            ctx['failed_count'] = sum(1 for s in summary if s['failed'])
            ctx['failed_percent'] = round(ctx['failed_count'] / len(summary) * 100) if summary else 0
        return ctx

    def sgpa_to_grade(self, sgpa):
        if sgpa >= 9: return 'A+'
        if sgpa >= 8: return 'A'
        if sgpa >= 7: return 'B+'
        if sgpa >= 6: return 'B'
        if sgpa >= 5: return 'C+'
        if sgpa >= 4: return 'C'
        if sgpa >= 3.3: return 'D'
        return 'F'


class ReportCardView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'results/report_card.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student = self.object
        branch = student.student_class.name
        current_sem = int(student.student_class.section.replace('Sem ', ''))
        ctx['current_sem'] = current_sem
        ctx['semesters'] = list(range(1, current_sem + 1))

        selected_sem = self.request.GET.get('sem')
        if selected_sem:
            try:
                selected_sem = int(selected_sem)
            except ValueError:
                selected_sem = current_sem
        else:
            selected_sem = current_sem
        ctx['selected_sem'] = selected_sem

        classes = Class.objects.filter(name=branch, section__in=[f'Sem {s}' for s in range(1, current_sem + 1)])

        exam_groups = {}
        results = Result.objects.filter(student=student).select_related('exam', 'subject')
        for r in results:
            exam_groups.setdefault(r.exam, []).append(r)
        for exam, rlist in exam_groups.items():
            total_obtained = sum(r.total_marks for r in rlist)
            total_max = sum(r.subject.max_marks for r in rlist)
            sgpa, total_credits = calculate_sgpa(rlist)
            rlist.append({
                'is_total_row': True,
                'total_obtained': round(total_obtained, 2),
                'total_max': total_max,
                'sgpa': sgpa,
                'total_credits': total_credits,
            })

        if selected_sem:
            exam_groups = {e: rl for e, rl in exam_groups.items()
                           if e.student_class.section == f'Sem {selected_sem}'}
        ctx['exam_groups'] = exam_groups
        return ctx


class SendResultsView(LoginRequiredMixin, View):
    def _send_single(self, student, exam, base_url):
        if not student.email:
            return 'skip'
        results = list(Result.objects.filter(student=student, exam=exam).select_related('subject'))
        if not results:
            return 'skip'

        total_marks = sum(r.total_marks for r in results)
        max_marks = sum(r.subject.max_marks for r in results)
        sgpa, total_credits = calculate_sgpa(results)
        failed = any(not r.is_pass for r in results)

        context = {
            'student': student,
            'exam': exam,
            'branch': student.student_class.name,
            'semester': student.student_class.section,
            'results': results,
            'total_marks': round(total_marks, 2),
            'max_marks': max_marks,
            'sgpa': sgpa,
            'total_credits': total_credits,
            'failed': failed,
            'result_portal_url': f'{base_url}/accounts/result-portal/',
        }

        pdf = render_to_pdf('results/emails/result_pdf.html', context)
        if pdf is None:
            return 'skip'

        try:
            email = EmailMessage(
                subject=f'Result Published - {exam.name}',
                body=f'Dear {student.full_name},\n\nYour result for {exam.name} is attached as PDF.\n\nRegards,\nMiracle Institute of Technology, Kanpur',
                from_email=settings.DEFAULT_FROM_EMAIL or None,
                to=[student.email],
            )
            email.attach(f'Result_{student.roll_number}_{exam.name}.pdf', pdf, 'application/pdf')
            email.send(fail_silently=False)
            return 'sent'
        except Exception:
            return 'skip'

    def post(self, request, *args, **kwargs):
        class_id = request.POST.get('class_id')
        exam_id = request.POST.get('exam_id')

        if not class_id or not exam_id:
            messages.error(request, 'Please select both a branch and an exam.')
            return redirect('results:class_summary')

        exam = get_object_or_404(Exam, pk=exam_id)
        students = Student.objects.filter(student_class_id=class_id, is_deleted=False)
        base_url = f'{request.scheme}://{request.get_host()}'

        sent = 0
        skipped = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self._send_single, s, exam, base_url) for s in students]
            for f in as_completed(futures):
                result = f.result()
                if result == 'sent':
                    sent += 1
                else:
                    skipped += 1

        msg = f'Results sent to {sent} student(s) via email.'
        if skipped:
            msg += f' {skipped} student(s) skipped (no email or no results).'
        messages.success(request, msg)
        return redirect(f'{reverse_lazy("results:class_summary")}?class={class_id}&exam={exam_id}')
