from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Sirf Admin access - Dashboard APIs
    """
    message = "Only admin users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class CanCreateAdmin(BasePermission):
    """
    Sirf Admin hi admin create kar sakta hai
    """
    message = "Only admin can create admin users."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )

