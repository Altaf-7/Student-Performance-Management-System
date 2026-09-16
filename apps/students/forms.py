from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import StudentProfile

User = get_user_model()


class StudentCreateForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    profile_photo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), help_text="Initial login password for this student.")

    class Meta:
        model = StudentProfile
        fields = ["student_id", "date_of_birth", "gender", "address", "department", "semester", "enrollment_year", "academic_status"]
        widgets = {
            "student_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. STU-2026-001"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "enrollment_year": forms.NumberInput(attrs={"class": "form-control"}),
            "academic_status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    @transaction.atomic
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data.get("last_name", ""),
            email=self.cleaned_data["email"],
            phone=self.cleaned_data.get("phone", ""),
            password=self.cleaned_data["password"],
            role=User.Role.STUDENT,
        )
        if self.cleaned_data.get("profile_photo"):
            user.profile_photo = self.cleaned_data["profile_photo"]
            user.save()
        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return profile


class StudentEditForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = StudentProfile
        fields = ["date_of_birth", "gender", "address", "department", "semester", "enrollment_year", "academic_status"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "enrollment_year": forms.NumberInput(attrs={"class": "form-control"}),
            "academic_status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["phone"].initial = self.instance.user.phone

    @transaction.atomic
    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.save()
        return profile
