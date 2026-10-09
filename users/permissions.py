
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Allows only POS Admins and Django superusers.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.role == "admin"
                or user.is_superuser
            )
        )


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return bool(
            user
            and user.is_authenticated
            and (user.role == "admin" or user.is_superuser)
        )


class IsAdminOrStaff(BasePermission):
    """
    Allows authenticated Admin or Django staff users.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.role == "admin"
                or user.is_staff
                or user.is_superuser
            )
        )


class IsOwnerOrAdminStaff(BasePermission):
    """
    Owners can update/delete their own objects.
    Admins and staff can update/delete all objects.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if (
            user.role == "admin"
            or user.is_staff
            or user.is_superuser
        ):
            return True

        return getattr(obj, "member_id", None) == user.pk