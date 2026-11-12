from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from accounts.models import User

def student_required(view_func):
    """
    Decorator for views that checks that the logged in user is a student,
    redirects to the log-in page if necessary.
    """
    def check_user(user):
        if not user.is_authenticated:
            return False
        if user.role == User.RoleChoices.STUDENT:
            return True
        raise PermissionDenied
    
    return user_passes_test(check_user, login_url='accounts:login')(view_func)

def faculty_required(view_func):
    """
    Decorator for views that checks that the logged in user is a faculty,
    redirects to the log-in page if necessary.
    """
    def check_user(user):
        if not user.is_authenticated:
            return False
        if user.role == User.RoleChoices.FACULTY:
            return True
        raise PermissionDenied
    
    return user_passes_test(check_user, login_url='accounts:login')(view_func)

def admin_required(view_func):
    """
    Decorator for views that checks that the logged in user is an admin,
    redirects to the log-in page if necessary.
    """
    def check_user(user):
        if not user.is_authenticated:
            return False
        if user.role == User.RoleChoices.ADMIN or user.is_superuser:
            return True
        raise PermissionDenied
    
    return user_passes_test(check_user, login_url='accounts:login')(view_func)
