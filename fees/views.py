import uuid
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView
from students.models import Student
from .models import FeeStructure, Payment


class FeeListView(ListView):
    model = FeeStructure
    template_name = 'fees/fee_list.html'
    context_object_name = 'fee_structures'


class StudentFeeListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'fees/student_fees.html'
    context_object_name = 'payments'

    def get_queryset(self):
        student_id = self.request.session.get('student_id')
        if student_id:
            return Payment.objects.filter(student_id=student_id).select_related('fee_structure')
        return Payment.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        if student_id:
            ctx['fee_structures'] = FeeStructure.objects.all()
            ctx['student'] = get_object_or_404(Student, pk=student_id)
            total_due = sum(fs.amount for fs in FeeStructure.objects.all())
            total_paid = sum(p.amount_paid for p in Payment.objects.filter(student_id=student_id))
            ctx['total_due'] = total_due
            ctx['total_paid'] = total_paid
            ctx['balance'] = total_due - total_paid
        return ctx


class FeePaymentView(LoginRequiredMixin, View):
    def get(self, request, pk):
        fee = get_object_or_404(FeeStructure, pk=pk)
        student_id = request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id) if student_id else None
        return render(request, 'fees/fee_payment.html', {'fee': fee, 'student': student})

    def post(self, request, pk):
        fee = get_object_or_404(FeeStructure, pk=pk)
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_portal')
        student = get_object_or_404(Student, pk=student_id)
        amount = request.POST.get('amount', fee.amount)
        Payment.objects.create(
            student=student,
            fee_structure=fee,
            amount_paid=amount,
            status='paid',
            transaction_id=f'TXN{uuid.uuid4().hex[:12].upper()}',
        )
        messages.success(request, f'Payment of ₹{amount} successful! Transaction ID: {Payment.objects.last().transaction_id}')
        return redirect('fees:student_fees')
