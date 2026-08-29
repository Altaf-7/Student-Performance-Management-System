from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an Admin."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'admin' and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access the admin dashboard.")
        return super().dispatch(request, *args, **kwargs)
