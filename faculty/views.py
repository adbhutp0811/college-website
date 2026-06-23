from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Faculty
from .forms import FacultyForm


class FacultyListView(LoginRequiredMixin, ListView):
    model = Faculty
    template_name = 'faculty/faculty_list.html'
    context_object_name = 'faculty_list'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('classes')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                models.Q(first_name__icontains=q) |
                models.Q(last_name__icontains=q) |
                models.Q(employee_id__icontains=q) |
                models.Q(email__icontains=q) |
                models.Q(designation__icontains=q)
            )
        dept = self.request.GET.get('department')
        if dept:
            qs = qs.filter(classes__name=dept)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Faculty.objects.values_list(
            'classes__name', flat=True
        ).distinct().order_by()
        ctx['departments'] = sorted(set(d for d in ctx['departments'] if d))
        return ctx


class FacultyCreateView(LoginRequiredMixin, CreateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'faculty/faculty_form.html'
    success_url = reverse_lazy('faculty:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Faculty'
        return ctx


class FacultyUpdateView(LoginRequiredMixin, UpdateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'faculty/faculty_form.html'
    success_url = reverse_lazy('faculty:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Faculty'
        return ctx


class FacultyDeleteView(LoginRequiredMixin, DeleteView):
    model = Faculty
    template_name = 'faculty/faculty_confirm_delete.html'
    success_url = reverse_lazy('faculty:list')
    context_object_name = 'faculty'
