from django import forms

from .models import Attendance


class AttendanceDateCourseForm(forms.Form):
    """Step 1: faculty picks course + date to mark attendance for."""
    course = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={"class": "form-select"}))
    date = forms.DateField(widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))

    def __init__(self, *args, **kwargs):
        faculty_user = kwargs.pop("faculty_user", None)
        super().__init__(*args, **kwargs)
        from apps.academics.models import Course
        qs = Course.objects.all()
        if faculty_user is not None and not faculty_user.is_admin_role:
            qs = qs.filter(faculty=faculty_user)
        self.fields["course"].queryset = qs
