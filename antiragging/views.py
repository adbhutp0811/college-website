from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView
from students.models import Student
from .models import AntiRaggingCommittee, AntiRaggingComplaint, AntiRaggingUndertaking


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.session.get('student_id') is not None


class HomeView(TemplateView):
    template_name = 'antiragging/home.html'


class CommitteeView(ListView):
    model = AntiRaggingCommittee
    template_name = 'antiragging/committee.html'
    context_object_name = 'members'

    def get_queryset(self):
        return AntiRaggingCommittee.objects.filter(is_active=True)


class UndertakingView(StudentRequiredMixin, TemplateView):
    template_name = 'antiragging/undertaking.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        undertaking = AntiRaggingUndertaking.objects.filter(student=student).first()
        ctx['student'] = student
        ctx['undertaking'] = undertaking
        return ctx


class SignUndertakingView(StudentRequiredMixin, View):
    def post(self, request):
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        if AntiRaggingUndertaking.objects.filter(student=student).exists():
            messages.info(request, 'You have already submitted your undertaking.')
        else:
            AntiRaggingUndertaking.objects.create(student=student, is_accepted=True, uploaded_file=request.FILES.get('uploaded_file'))
            messages.success(request, 'Anti-ragging undertaking submitted successfully.')
        return redirect('antiragging:undertaking')


class SubmitComplaintView(StudentRequiredMixin, View):
    template_name = 'antiragging/submit_complaint.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        AntiRaggingComplaint.objects.create(
            student=student if not is_anonymous else None,
            category=request.POST.get('category'),
            subject=request.POST.get('subject', ''),
            description=request.POST.get('description', ''),
            is_anonymous=is_anonymous,
        )
        messages.success(request, 'Complaint submitted. The committee will review it shortly.')
        return redirect('antiragging:complaint_list')


class ComplaintListView(StudentRequiredMixin, ListView):
    template_name = 'antiragging/complaint_list.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        student_id = self.request.session.get('student_id')
        return AntiRaggingComplaint.objects.filter(student_id=student_id)


class StaffComplaintListView(StaffRequiredMixin, ListView):
    template_name = 'antiragging/staff_complaints.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        return AntiRaggingComplaint.objects.all().select_related('student').order_by('-created_at')


class ResolveComplaintView(StaffRequiredMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(AntiRaggingComplaint, pk=pk)
        status = request.POST.get('status')
        response_text = request.POST.get('admin_response', '')
        if status in ['investigating', 'resolved', 'dismissed']:
            complaint.status = status
            complaint.admin_response = response_text
            if status == 'resolved':
                complaint.resolved_at = timezone.now()
            complaint.save()
            messages.success(request, f'Complaint status updated to {status}.')
        return redirect('antiragging:staff_complaints')
