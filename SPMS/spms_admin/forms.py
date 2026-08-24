from django import forms
from accounts.models import User
from students.models import Student
from academics.models import Department, Course, CourseBatch, Semester

class StudentCreateForm(forms.Form):
    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    
    # Student fields
    enrollment_no = forms.CharField(max_length=50, required=True)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Student.GenderChoices.choices, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    guardian_name = forms.CharField(max_length=100, required=False)
    guardian_contact = forms.CharField(max_length=20, required=False)
    emergency_contact = forms.CharField(max_length=20, required=False)
    
    # Academic fields
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)
    batch = forms.ModelChoiceField(queryset=CourseBatch.objects.all(), required=True)
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=True)
    admission_year = forms.IntegerField(required=True, help_text="e.g. 2025")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists.")
        return email

    def clean_enrollment_no(self):
        eno = self.cleaned_data['enrollment_no']
        if Student.objects.filter(enrollment_no=eno).exists():
            raise forms.ValidationError("Student with this enrollment number already exists.")
        return eno
        
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        batch = cleaned_data.get('batch')
        semester = cleaned_data.get('semester')
        
        if batch and course and batch.course != course:
            self.add_error('batch', "Selected batch does not belong to the selected course.")
            
        if semester and batch and semester.course_batch != batch:
            self.add_error('semester', "Selected semester does not belong to the selected batch.")
            
        return cleaned_data

class FacultyCreateForm(forms.Form):
    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    
    # Faculty Profile
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    designation = forms.CharField(max_length=100, required=True)
    specialization = forms.CharField(max_length=150, required=False)
    qualification = forms.CharField(max_length=150, required=False)
    office_email = forms.EmailField(required=False)
    office_contact = forms.CharField(max_length=20, required=False)
    date_of_join = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists.")
        return email
