from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrManagerOrReadOnly(BasePermission):
    """
    Anyone can view products and categories.
    Only Admin and Manager can create, update, or delete them.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.role in ["admin", "manager"]
                or user.is_superuser
            )
        )
