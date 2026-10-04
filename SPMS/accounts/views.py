from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from accounts.forms import CustomAuthenticationForm
from accounts.models import User

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
