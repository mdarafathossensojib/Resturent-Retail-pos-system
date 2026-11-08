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


class IsAdminOrManagerForStockAdjustment(BasePermission):
    """
    Only Admin and Manager can manually adjust stock.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.role in ["admin", "manager"]
                or user.is_superuser
            )
        )