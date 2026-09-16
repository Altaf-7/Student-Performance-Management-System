class RoleRedirectMiddleware:
    """Lightweight pass-through middleware placeholder.

    Role-based access control is enforced at the view layer through
    apps.accounts.permissions mixins/decorators, not here. This
    middleware is kept as an extension point (e.g. for forcing a
    password change on first login) without adding hidden magic to
    every request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
