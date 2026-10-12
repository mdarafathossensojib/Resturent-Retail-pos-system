from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminManagerOrCashierForSales(BasePermission):
    """
    Authenticated Admins, Managers and Cashiers can view sales
    and create sales. Updating and deleting are handled separately.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.role not in ["admin", "manager", "cashier"]:
            return False

        return request.method in SAFE_METHODS or view.action == "create"
