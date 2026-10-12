from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    """
    Only authenticated Admins and Managers can access purchases.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.role in ["admin", "manager"]
            )
        )

class IsAuthenticatedReadOnly(BasePermission):
    """
    Allow read-only access to authenticated users.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and request.method in ["GET", "HEAD", "OPTIONS"]
        )
