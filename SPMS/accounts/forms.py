from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.db import transaction
from students.models import Student

User = get_user_model()

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    enrollment_no = forms.CharField(max_length=50, required=True)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Student.GenderChoices.choices, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'contact_number')

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
