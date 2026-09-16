from django import forms

from .models import Assignment, AssignmentSubmission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "course", "attachment", "due_date", "maximum_marks"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "due_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "maximum_marks": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        faculty_user = kwargs.pop("faculty_user", None)
        super().__init__(*args, **kwargs)
        if faculty_user is not None and not faculty_user.is_admin_role:
            from apps.academics.models import Course
            self.fields["course"].queryset = Course.objects.filter(faculty=faculty_user)


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ["file"]
        widgets = {"file": forms.ClearableFileInput(attrs={"class": "form-control"})}


class GradeSubmissionForm(forms.Form):
    marks_obtained = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control"}))
    feedback = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
