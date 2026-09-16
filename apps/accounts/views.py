from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from .forms import SPMSAuthenticationForm, ProfileUpdateForm, SPMSPasswordChangeForm
from .models import User


class SPMSLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = SPMSAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().get_full_name() or form.get_user().username}!")
        return super().form_valid(form)


class SPMSLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("accounts:login")


@login_required
def role_redirect(request):
    """Single entry point after login: sends each role to its dashboard."""
    return redirect(request.user.get_dashboard_url())


class SPMSPasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class SPMSPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class SPMSPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class SPMSPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class SPMSPasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = SPMSPasswordChangeForm
    success_url = reverse_lazy("accounts:password_change_done")


class SPMSPasswordChangeDoneView(LoginRequiredMixin, auth_views.PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_role:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    from apps.analytics.services import get_admin_dashboard_context
    context = get_admin_dashboard_context()
    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
def faculty_dashboard(request):
    if not (request.user.is_faculty_role or request.user.is_admin_role):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    from apps.analytics.services import get_faculty_dashboard_context
    context = get_faculty_dashboard_context(request.user)
    return render(request, "dashboard/faculty_dashboard.html", context)


@login_required
def student_dashboard(request):
    if not request.user.is_student_role:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    from apps.analytics.services import get_student_dashboard_context
    context = get_student_dashboard_context(request.user)
    return render(request, "dashboard/student_dashboard.html", context)
