from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.views import View
from .models import ExamRegistration


class ExamFormCreateView(LoginRequiredMixin, CreateView):
    model = ExamRegistration
    fields = ['semester', 'academic_year', 'subjects']
    template_name = 'exam_forms/exam_form.html'
    success_url = reverse_lazy('exam_forms:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from results.models import Subject
        form.fields['subjects'].queryset = Subject.objects.all()
        form.fields['subjects'].widget.attrs['size'] = '10'
        form.fields['subjects'].help_text = 'Hold Ctrl to select multiple subjects'
        return form

    def form_valid(self, form):
        from students.models import Student
        student = get_object_or_404(Student, pk=self.request.session.get('student_id'))
        form.instance.student = student
        messages.success(self.request, 'Exam form submitted successfully!')
        return super().form_valid(form)


class ExamFormListView(LoginRequiredMixin, ListView):
    model = ExamRegistration
    template_name = 'exam_forms/exam_list.html'
    context_object_name = 'registrations'

    def get_queryset(self):
        from students.models import Student
        student_id = self.request.session.get('student_id')
        if student_id:
            return ExamRegistration.objects.filter(student_id=student_id).prefetch_related('subjects')
        return ExamRegistration.objects.none()


class StaffExamFormListView(LoginRequiredMixin, ListView):
    model = ExamRegistration
    template_name = 'exam_forms/staff_exam_list.html'
    context_object_name = 'registrations'
    paginate_by = 20

    def get_queryset(self):
        qs = ExamRegistration.objects.select_related('student__student_class').prefetch_related('subjects')
        status = self.request.GET.get('status', '')
        semester = self.request.GET.get('semester', '')
        if status:
            qs = qs.filter(status=status)
        if semester:
            qs = qs.filter(semester=semester)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_semester'] = self.request.GET.get('semester', '')
        return ctx


class ExamFormApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reg = get_object_or_404(ExamRegistration, pk=pk)
        action = request.POST.get('action', '')
        if action == 'approve':
            reg.status = 'approved'
        elif action == 'reject':
            reg.status = 'rejected'
        reg.remarks = request.POST.get('remarks', '')
        reg.save()
        messages.success(request, f'Exam form {reg.status} successfully!')
        return redirect('exam_forms:staff_list')
