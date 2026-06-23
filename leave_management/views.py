from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View
from django.views.generic.edit import FormView
from django import forms
from .models import LeaveApplication


class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'from_date', 'to_date', 'reason']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'to_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ApplyLeaveView(View):
    template_name = 'leave_management/apply_leave.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LeaveApplicationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        from students.models import Student
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            student = get_object_or_404(Student, pk=request.session['student_id'])
            leave = form.save(commit=False)
            leave.student = student
            leave.save()
            messages.success(request, 'Leave application submitted successfully!')
            return redirect('leave_management:my_leaves')
        return render(request, self.template_name, {'form': form})


class MyLeavesView(ListView):
    model = LeaveApplication
    template_name = 'leave_management/my_leaves.html'
    context_object_name = 'leaves'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return LeaveApplication.objects.filter(student_id=self.request.session['student_id'])


class StaffLeaveListView(LoginRequiredMixin, ListView):
    model = LeaveApplication
    template_name = 'leave_management/staff_leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 20

    def get_queryset(self):
        qs = LeaveApplication.objects.select_related('student__student_class')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_status'] = self.request.GET.get('status', '')
        return ctx


class UpdateLeaveStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        leave = get_object_or_404(LeaveApplication, pk=pk)
        action = request.POST.get('action')
        remark = request.POST.get('admin_remark', '')

        if action == 'approved':
            leave.status = 'approved'
            leave.approved_by = request.user
            messages.success(request, f'Leave #{pk} approved.')
        elif action == 'rejected':
            leave.status = 'rejected'
            leave.approved_by = request.user
            messages.success(request, f'Leave #{pk} rejected.')
        else:
            messages.error(request, 'Invalid action.')
            return redirect('leave_management:staff_list')

        leave.admin_remark = remark
        leave.save()
        return redirect('leave_management:staff_list')
