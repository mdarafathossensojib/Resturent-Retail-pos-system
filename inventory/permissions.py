from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedReadOnly(BasePermission):
    """
    Authenticated users can view records but cannot modify them.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and request.method in SAFE_METHODS
        )
