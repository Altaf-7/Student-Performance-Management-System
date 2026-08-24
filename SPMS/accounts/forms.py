from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.db import transaction
from students.models import Student
from faculty.models import Faculty
from academics.models import Department

User = get_user_model()

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    enrollment_no = forms.CharField(max_length=50, required=True)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('', 'Select Gender')] + Student.GenderChoices.choices, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'contact_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email Address'})
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'Contact Number (Optional)'})
        self.fields['enrollment_no'].widget.attrs.update({'placeholder': 'Enrollment Number'})
        
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': 'Password confirmation'})

    def clean_enrollment_no(self):
        enrollment_no = self.cleaned_data.get('enrollment_no')
        if Student.objects.filter(enrollment_no=enrollment_no).exists():
            raise forms.ValidationError("A student with this enrollment number already exists.")
        return enrollment_no

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = User.RoleChoices.STUDENT
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        
        # Create the associated student profile
        student = Student.objects.create(
            user=user,
            enrollment_no=self.cleaned_data.get('enrollment_no'),
            date_of_birth=self.cleaned_data.get('date_of_birth'),
            gender=self.cleaned_data.get('gender')
        )
        return user

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': True, 'placeholder': 'Email address'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})

class FacultySignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    
    # Faculty specific fields
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    designation = forms.CharField(max_length=100, required=True)
    specialization = forms.CharField(max_length=150, required=False)
    qualification = forms.CharField(max_length=150, required=False)
    office_email = forms.EmailField(required=False)
    office_contact = forms.CharField(max_length=20, required=False)
    date_of_join = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'contact_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'placeholder': self.fields[field].label})
            
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = User.RoleChoices.FACULTY
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        
        Faculty.objects.create(
            user=user,
            department=self.cleaned_data.get('department'),
            designation=self.cleaned_data.get('designation'),
            specialization=self.cleaned_data.get('specialization'),
            qualification=self.cleaned_data.get('qualification'),
            office_email=self.cleaned_data.get('office_email'),
            office_contact=self.cleaned_data.get('office_contact'),
            date_of_join=self.cleaned_data.get('date_of_join')
        )
        return user
