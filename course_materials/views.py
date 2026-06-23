from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django import forms
from students.models import Class, Student
from results.models import Subject
from .models import StudyMaterial, Assignment, Submission


class MaterialListView(ListView):
    model = StudyMaterial
    template_name = 'course_materials/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        qs = StudyMaterial.objects.filter(is_published=True)
        class_id = self.request.GET.get('class', '')
        subject_id = self.request.GET.get('subject', '')
        if class_id:
            qs = qs.filter(student_class_id=class_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs.select_related('subject', 'student_class', 'uploaded_by')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        ctx['subjects'] = Subject.objects.all()
        ctx['current_class'] = self.request.GET.get('class', '')
        ctx['current_subject'] = self.request.GET.get('subject', '')
        return ctx


class MaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'subject', 'student_class', 'material_type', 'file', 'external_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'material_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control'}),
        }


class MaterialCreateView(LoginRequiredMixin, CreateView):
    model = StudyMaterial
    form_class = MaterialForm
    template_name = 'course_materials/material_form.html'
    success_url = reverse_lazy('course_materials:material_list')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Study material created successfully!')
        return super().form_valid(form)


class AssignmentListView(ListView):
    model = Assignment
    template_name = 'course_materials/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        qs = Assignment.objects.filter(is_active=True)
        class_id = self.request.GET.get('class', '')
        subject_id = self.request.GET.get('subject', '')
        if class_id:
            qs = qs.filter(student_class_id=class_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs.select_related('subject', 'student_class', 'created_by')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        ctx['subjects'] = Subject.objects.all()
        ctx['current_class'] = self.request.GET.get('class', '')
        ctx['current_subject'] = self.request.GET.get('subject', '')
        return ctx


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'student_class', 'max_marks', 'due_date', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'course_materials/assignment_form.html'
    success_url = reverse_lazy('course_materials:assignment_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Assignment created successfully!')
        return super().form_valid(form)


class SubmitAssignmentView(View):
    template_name = 'course_materials/submit_assignment.html'

    def get(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk, is_active=True)
        student_id = request.session.get('student_id')
        existing = None
        if student_id:
            existing = Submission.objects.filter(assignment=assignment, student_id=student_id).first()
        return render(request, self.template_name, {
            'assignment': assignment,
            'existing': existing,
            'student_id': student_id,
        })

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk, is_active=True)
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login as a student first.')
            return redirect('accounts:student_login')
        student = get_object_or_404(Student, pk=student_id)
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={'file': request.FILES.get('file')}
        )
        if not created:
            submission.file = request.FILES.get('file')
            submission.remarks = request.POST.get('remarks', '')
            submission.save()
            messages.success(request, 'Assignment resubmitted successfully!')
        else:
            submission.remarks = request.POST.get('remarks', '')
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
        return redirect('course_materials:my_submissions')


from django.shortcuts import render


class MySubmissionsView(TemplateView):
    template_name = 'course_materials/my_submissions.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        if student_id:
            ctx['submissions'] = Submission.objects.filter(student_id=student_id).select_related('assignment', 'assignment__subject')
        else:
            ctx['submissions'] = Submission.objects.none()
        return ctx


class StaffSubmissionsView(LoginRequiredMixin, ListView):
    template_name = 'course_materials/staff_submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        self.assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        return Submission.objects.filter(assignment=self.assignment).select_related('student')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['assignment'] = self.assignment
        return ctx


class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['obtained_marks', 'feedback']
        widgets = {
            'obtained_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GradeSubmissionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
        return redirect('course_materials:staff_submissions', pk=submission.assignment_id)
