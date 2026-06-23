from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.views import View
from .models import Grievance


class GrievanceCreateView(LoginRequiredMixin, CreateView):
    model = Grievance
    fields = ['category', 'subject', 'description', 'is_anonymous']
    template_name = 'grievances/grievance_form.html'
    success_url = reverse_lazy('grievances:list')

    def form_valid(self, form):
        from students.models import Student
        student = get_object_or_404(Student, pk=self.request.session.get('student_id'))
        form.instance.student = student
        messages.success(self.request, 'Grievance submitted successfully!')
        return super().form_valid(form)


class GrievanceListView(LoginRequiredMixin, ListView):
    model = Grievance
    template_name = 'grievances/grievance_list.html'
    context_object_name = 'grievances'
    paginate_by = 20

    def get_queryset(self):
        from students.models import Student
        student_id = self.request.session.get('student_id')
        if student_id:
            return Grievance.objects.filter(student_id=student_id)
        return Grievance.objects.none()


class StaffGrievanceListView(LoginRequiredMixin, ListView):
    model = Grievance
    template_name = 'grievances/staff_grievance_list.html'
    context_object_name = 'grievances'
    paginate_by = 20

    def get_queryset(self):
        qs = Grievance.objects.select_related('student__student_class')
        status = self.request.GET.get('status', '')
        category = self.request.GET.get('category', '')
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_category'] = self.request.GET.get('category', '')
        return ctx


class GrievanceResolveView(LoginRequiredMixin, UpdateView):
    model = Grievance
    fields = ['status', 'admin_response']
    template_name = 'grievances/grievance_resolve.html'
    success_url = reverse_lazy('grievances:staff_list')

    def form_valid(self, form):
        if form.instance.status == 'resolved':
            form.instance.resolved_at = timezone.now()
        messages.success(self.request, 'Grievance updated successfully!')
        return super().form_valid(form)
