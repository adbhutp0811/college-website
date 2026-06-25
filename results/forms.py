from django import forms
from .models import Exam, Result, Subject


class ResultForm(forms.Form):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class BulkResultForm(forms.Form):
    def __init__(self, *args, students=None, subject=None, exam=None, **kwargs):
        super().__init__(*args, **kwargs)
        if students and subject:
            for student in students:
                existing = Result.objects.filter(
                    student=student, subject=subject, exam=exam
                ).first()
                i_val = existing.internal_marks if existing else ''
                e_val = existing.external_marks if existing else ''
                self.fields[f'internal_marks_{student.id}'] = forms.FloatField(
                    required=False,
                    initial=i_val,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm marks-input mark-internal',
                        'placeholder': 'Internal',
                        'data-sid': student.id,
                    }),
                    label=f'{student.first_name} {student.last_name} ({student.roll_number}) - Internal',
                )
                self.fields[f'external_marks_{student.id}'] = forms.FloatField(
                    required=False,
                    initial=e_val,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm marks-input mark-external',
                        'placeholder': 'External',
                        'data-sid': student.id,
                    }),
                    label=f'{student.first_name} {student.last_name} ({student.roll_number}) - External',
                )
