from django.views.generic import ListView, DetailView
from .models import Company, PlacementDrive

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
