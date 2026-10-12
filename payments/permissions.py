from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminManagerOrCashierForPayments(BasePermission):
    """
    Admin, Manager and Cashier can view and create payments.
    Updating and deleting payments are not permitted.
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
