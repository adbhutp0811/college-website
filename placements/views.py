from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib import messages
from .models import Company, PlacementDrive, PlacementApplication
from students.models import Student

LOGO_MAP = {
    'TCS': 'tcs', 'Infosys': 'infosys', 'Wipro': 'wipro',
    'Accenture': 'accenture', 'Amazon': 'amazon', 'HCL Technologies': 'hcl',
    'Google': 'google', 'Microsoft': 'microsoft', 'Flipkart': 'flipkart',
    'Adobe': 'adobe', 'Mahindra & Mahindra': 'mahindra', 'Larsen & Toubro': 'lnt',
    'Cognizant': 'cognizant', 'Capgemini': 'capgemini', 'IBM': 'ibm',
    'Tech Mahindra': 'techmahindra', 'Deloitte': 'deloitte', 'LTIMindtree': 'lti',
}

class CompanyListView(ListView):
    model = Company
    template_name = 'placements/company_list.html'
    context_object_name = 'companies'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        for c in ctx['companies']:
            c.logo_key = LOGO_MAP.get(c.name, '')
        return ctx


class PlacementDriveListView(ListView):
    model = PlacementDrive
    template_name = 'placements/drive_list.html'
    context_object_name = 'drives'

    def get_queryset(self):
        return PlacementDrive.objects.filter(is_active=True)


class PlacementDriveDetailView(DetailView):
    model = PlacementDrive
    template_name = 'placements/drive_detail.html'
    context_object_name = 'drive'
    slug_field = 'pk'


class ApplyDriveView(View):
    def post(self, request, pk):
        drive = get_object_or_404(PlacementDrive, pk=pk, is_active=True)
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login as student first.')
            return redirect('accounts:student_login')
        student = get_object_or_404(Student, id=student_id)
        if PlacementApplication.objects.filter(drive=drive, student=student).exists():
            messages.warning(request, 'You have already applied for this drive.')
            return redirect('placements:drive_detail', pk=pk)
        PlacementApplication.objects.create(drive=drive, student=student)
        messages.success(request, f'Successfully applied for {drive.company.name} - {drive.title}!')
        return redirect('placements:my_applications')


class MyApplicationsView(TemplateView):
    template_name = 'placements/my_applications.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            ctx['applications'] = PlacementApplication.objects.filter(student=student).select_related('drive__company')
        return ctx


class StaffApplicationsView(LoginRequiredMixin, ListView):
    model = PlacementApplication
    template_name = 'placements/staff_applications.html'
    context_object_name = 'applications'
    paginate_by = 50

    def get_queryset(self):
        qs = PlacementApplication.objects.all().select_related('student', 'drive__company')
        drive_id = self.request.GET.get('drive_id')
        if drive_id:
            qs = qs.filter(drive_id=drive_id)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['drives'] = PlacementDrive.objects.filter(is_active=True)
        ctx['statuses'] = PlacementApplication.STATUS_CHOICES
        return ctx


class UpdateApplicationStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        app = get_object_or_404(PlacementApplication, pk=pk)
        status = request.POST.get('status')
        if status in dict(PlacementApplication.STATUS_CHOICES):
            app.status = status
            app.save()
            messages.success(request, f'Application status updated to {app.get_status_display()}.')
        return redirect('placements:staff_applications')
