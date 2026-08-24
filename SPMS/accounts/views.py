from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

from accounts.forms import StudentSignUpForm, CustomAuthenticationForm, FacultySignUpForm
from accounts.models import User
from django.utils.decorators import method_decorator
from accounts.decorators import admin_required

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'authentication/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.role == User.RoleChoices.STUDENT:
            return reverse_lazy('students:dashboard')
        elif user.role == User.RoleChoices.FACULTY:
            return reverse_lazy('faculty:dashboard')
        elif user.role == User.RoleChoices.ADMIN or user.is_superuser:
            return reverse_lazy('spms_admin:dashboard')
        else:
            return super().get_success_url()

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'authentication/signup.html'
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful. Welcome!')
        return redirect('students:dashboard')

@method_decorator(admin_required, name='dispatch')
class FacultySignUpView(CreateView):
    model = User
    form_class = FacultySignUpForm
    template_name = 'authentication/signup.html'
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'faculty'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f'Faculty account for {user.get_full_name()} created successfully.')
        return redirect('spms_admin:dashboard')
