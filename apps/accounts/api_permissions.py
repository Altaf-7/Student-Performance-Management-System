from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)


class IsFacultyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_faculty_role or u.is_admin_role))


class IsFacultyOrAdminOrReadOnlyStudent(BasePermission):
    """Students can only read (GET/HEAD/OPTIONS); faculty/admin can write."""

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return u.is_faculty_role or u.is_admin_role
