from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from students.models import Student
from .models import ScholarshipApplication, ScholarshipScheme


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.session.get('student_id') is not None


class SchemeListView(ListView):
    model = ScholarshipScheme
    template_name = 'scholarships/scheme_list.html'
    context_object_name = 'schemes'

    def get_queryset(self):
        return ScholarshipScheme.objects.filter(is_active=True)


class SchemeDetailView(DetailView):
    model = ScholarshipScheme
    template_name = 'scholarships/scheme_detail.html'
    context_object_name = 'scheme'


class ApplyScholarshipView(StudentRequiredMixin, View):
    def get(self, request, pk):
        scheme = get_object_or_404(ScholarshipScheme, pk=pk, is_active=True)
        student_id = request.session.get('student_id')
        existing = ScholarshipApplication.objects.filter(student_id=student_id, scheme=scheme).first()
        return render(request, 'scholarships/apply.html', {'scheme': scheme, 'existing': existing})

    def post(self, request, pk):
        scheme = get_object_or_404(ScholarshipScheme, pk=pk, is_active=True)
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        if ScholarshipApplication.objects.filter(student=student, scheme=scheme).exists():
            messages.error(request, 'You have already applied for this scheme.')
        else:
            ScholarshipApplication.objects.create(
                student=student,
                scheme=scheme,
                status='submitted',
                documents=request.FILES.get('documents'),
                remarks=request.POST.get('remarks', ''),
            )
            messages.success(request, 'Application submitted successfully.')
        return redirect('scholarships:my_applications')


class MyApplicationsView(StudentRequiredMixin, ListView):
    template_name = 'scholarships/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return ScholarshipApplication.objects.filter(student_id=self.request.session.get('student_id')).select_related('scheme')


class StaffApplicationListView(StaffRequiredMixin, ListView):
    template_name = 'scholarships/staff_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return ScholarshipApplication.objects.all().select_related('student', 'scheme').order_by('-applied_at')


class ReviewApplicationView(StaffRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(ScholarshipApplication, pk=pk)
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        if status in ['approved', 'rejected']:
            application.status = status
            application.remarks = remarks
            application.save()
            messages.success(request, f'Application {status} successfully.')
        return redirect('scholarships:staff_list')
