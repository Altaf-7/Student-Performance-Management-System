from django import forms

from .models import Department, Semester, Course, Enrollment


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "head_of_department", "description", "contact_email"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in ["name", "code", "contact_email"]}
        widgets["description"] = forms.Textarea(attrs={"class": "form-control", "rows": 3})
        widgets["head_of_department"] = forms.Select(attrs={"class": "form-select"})


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ["name", "semester_number", "academic_year", "start_date", "end_date", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "semester_number": forms.NumberInput(attrs={"class": "form-control"}),
            "academic_year": forms.TextInput(attrs={"class": "form-control", "placeholder": "2025-2026"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["course_code", "course_name", "description", "credits", "department", "semester", "faculty", "status"]
        widgets = {
            "course_code": forms.TextInput(attrs={"class": "form-control"}),
            "course_name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "credits": forms.NumberInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "faculty": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        self.fields["faculty"].queryset = get_user_model().objects.filter(role="FACULTY")


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "semester", "academic_year", "status"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.TextInput(attrs={"class": "form-control", "placeholder": "2025-2026"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        self.fields["student"].queryset = get_user_model().objects.filter(role="STUDENT")

    def clean(self):
        cleaned = super().clean()
        student, course, year = cleaned.get("student"), cleaned.get("course"), cleaned.get("academic_year")
        if student and course and year:
            qs = Enrollment.objects.filter(student=student, course=course, academic_year=year)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This student is already enrolled in this course for this academic year.")
        return cleaned
