from rest_framework.permissions import BasePermission
from rest_framework import permissions
from django.utils import timezone


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
    

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAdminOrStaff(BasePermission):
    """
    Allows access to Admin OR Staff users
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )
    



class IsOwnerOrAdminStaff(BasePermission):
    """
    Object-level permission:
    - Owner (member) can update/delete only own feedback
    - Admin/Staff can update/delete all feedback
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.member == request.user