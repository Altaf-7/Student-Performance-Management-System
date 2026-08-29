from django.contrib.auth.mixins import AccessMixin
from accounts.models import User
from django.core.exceptions import PermissionDenied

class StudentRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a student."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != User.RoleChoices.STUDENT:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class FacultyRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a faculty."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != User.RoleChoices.FACULTY:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an admin."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != User.RoleChoices.ADMIN and not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
