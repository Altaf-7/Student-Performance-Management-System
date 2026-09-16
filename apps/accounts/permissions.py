"""
Central, server-side role enforcement.

Every view that needs restricting must use one of these mixins/decorators.
Frontend hiding of buttons/links is cosmetic only - these are what actually
stop unauthorized access, returning 403 (PermissionDenied) when a role
check fails.
"""
from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows Super Admin and Admin only."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_role

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Admin privileges are required for this action.")


class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows Super Admin only (system-level operations)."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_super_admin

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Super Admin privileges are required for this action.")


class FacultyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows Faculty (and Admins, who can oversee faculty areas)."""

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_faculty_role or u.is_admin_role)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Faculty privileges are required for this action.")


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows Student only."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student_role

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("This page is only available to students.")


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_admin_role:
            raise PermissionDenied("Admin privileges are required for this action.")
        return view_func(request, *args, **kwargs)
    return _wrapped


def faculty_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_faculty_role or request.user.is_admin_role):
            raise PermissionDenied("Faculty privileges are required for this action.")
        return view_func(request, *args, **kwargs)
    return _wrapped


def student_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_student_role:
            raise PermissionDenied("This action is only available to students.")
        return view_func(request, *args, **kwargs)
    return _wrapped
