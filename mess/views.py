import uuid
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView
from students.models import Student
from .models import MessComplaint, MessFeePeriod, MessMenu, MessPayment


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.session.get('student_id') is not None


class MessHomeView(TemplateView):
    template_name = 'mess/home.html'


class MenuView(ListView):
    model = MessMenu
    template_name = 'mess/menu.html'
    context_object_name = 'menus'

    def get_queryset(self):
        return MessMenu.objects.filter(is_active=True)


class MessFeeView(StudentRequiredMixin, ListView):
    template_name = 'mess/fees.html'
    context_object_name = 'fee_periods'

    def get_queryset(self):
        return MessFeePeriod.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        ctx['payments'] = MessPayment.objects.filter(student_id=student_id).select_related('fee_period')
        ctx['student'] = get_object_or_404(Student, pk=student_id)
        return ctx


class PayMessFeeView(StudentRequiredMixin, View):
    def post(self, request, pk):
        period = get_object_or_404(MessFeePeriod, pk=pk, is_active=True)
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        if MessPayment.objects.filter(student=student, fee_period=period).exists():
            messages.error(request, 'You have already paid for this period.')
        else:
            MessPayment.objects.create(
                student=student,
                fee_period=period,
                status='paid',
                paid_at=timezone.now(),
                transaction_id=f'MESS{uuid.uuid4().hex[:12].upper()}',
            )
            messages.success(request, f'Mess fee of ₹{period.amount} paid successfully.')
        return redirect('mess:fees')


class ComplaintListView(StudentRequiredMixin, ListView):
    template_name = 'mess/complaints.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        return MessComplaint.objects.filter(student_id=self.request.session.get('student_id'))


class SubmitComplaintView(StudentRequiredMixin, View):
    template_name = 'mess/submit_complaint.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        MessComplaint.objects.create(
            student=student,
            category=request.POST.get('category'),
            subject=request.POST.get('subject', ''),
            description=request.POST.get('description', ''),
        )
        messages.success(request, 'Complaint submitted successfully.')
        return redirect('mess:complaints')


class StaffComplaintListView(StaffRequiredMixin, ListView):
    template_name = 'mess/staff_complaints.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        return MessComplaint.objects.all().select_related('student').order_by('-created_at')


class ResolveComplaintView(StaffRequiredMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(MessComplaint, pk=pk)
        complaint.is_resolved = True
        complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, 'Complaint marked as resolved.')
        return redirect('mess:staff_complaints')
