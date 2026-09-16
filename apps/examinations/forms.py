from django import forms

from .models import Examination, ExamResult


class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = ["name", "exam_type", "course", "semester", "academic_year", "exam_date", "maximum_marks", "description", "is_published"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.TextInput(attrs={"class": "form-control", "placeholder": "2025-2026"}),
            "exam_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "maximum_marks": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        faculty_user = kwargs.pop("faculty_user", None)
        super().__init__(*args, **kwargs)
        if faculty_user is not None and not faculty_user.is_admin_role:
            from apps.academics.models import Course
            self.fields["course"].queryset = Course.objects.filter(faculty=faculty_user)


class ExamResultEntryForm(forms.Form):
    obtained_marks = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control result-marks"}))
    remarks = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
