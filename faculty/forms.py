from django import forms
from .models import Faculty


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = [
            'employee_id', 'first_name', 'last_name', 'designation',
            'qualification', 'specialization', 'email', 'phone',
            'experience', 'profile_pic', 'classes', 'joining_date', 'is_active',
        ]
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'specialization': forms.Textarea(attrs={'rows': 3}),
            'classes': forms.SelectMultiple(attrs={'size': 10}),
        }
