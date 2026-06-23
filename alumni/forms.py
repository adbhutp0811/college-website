from django import forms
from .models import Alumni, AlumniEvent, Donation


class AlumniRegistrationForm(forms.ModelForm):
    class Meta:
        model = Alumni
        fields = ['first_name', 'last_name', 'email', 'phone', 'graduation_year', 'program',
                  'current_occupation', 'company', 'location', 'linkedin_url', 'photo', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/your-profile'}),
        }


class AlumniProfileForm(forms.ModelForm):
    class Meta:
        model = Alumni
        fields = ['first_name', 'last_name', 'email', 'phone', 'graduation_year', 'program',
                  'current_occupation', 'company', 'location', 'linkedin_url', 'photo', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/your-profile'}),
        }


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donor_name', 'donor_email', 'amount', 'purpose', 'transaction_id', 'payment_method', 'is_anonymous']
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 2}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = AlumniEvent
        fields = ['title', 'description', 'date', 'time', 'location', 'is_online', 'meeting_link',
                  'registration_deadline', 'max_participants', 'is_published']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'registration_deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
