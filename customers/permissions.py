from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsAdminManagerOrCashierForCustomer(BasePermission):
    """
    Admin and Manager can perform all customer operations.
    Cashiers can view, create, and update customers, but cannot delete.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.role in ["admin", "manager"]:
            return True

        if user.role == "cashier":
            return request.method in SAFE_METHODS or view.action in [
                "create",
                "update",
                "partial_update",
            ]

        return False
