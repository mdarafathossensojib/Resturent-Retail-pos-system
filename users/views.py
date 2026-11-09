from rest_framework.viewsets import ModelViewSet
from users.models import User
from users.serializers import UserCRUDSerializer
from users.permissions import IsAdmin
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import transaction
from notifications.services import notify_roles


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserCRUDSerializer
    permission_classes = [IsAdmin]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["role", "is_active", "gender"]

    search_fields = [
        "email",
        "first_name",
        "last_name",
        "phone_number",
    ]

    ordering_fields = [
        "date_joined",
        "last_login",
        "first_name",
        "email",
    ]

    ordering = ["-date_joined"]

    def perform_create(self, serializer):
        user = serializer.save()

        notify_roles(
            roles=["admin"],
            title="New User Created",
            message=(
                f"A new user account has been created. "
                f"Email: {user.email}, Role: {user.role}."
            ),
            notification_type="system",
            related_url=f"/users/{user.pk}",
            exclude_users=[self.request.user],
        )


    def perform_update(self, serializer):
        user = self.get_object()

        old_role = user.role
        old_active = user.is_active

        new_role = serializer.validated_data.get("role", old_role)
        new_active = serializer.validated_data.get("is_active", old_active)

        if user.role == "admin" and user.is_active:
            removing_admin = new_role != "admin" or not new_active

            if removing_admin:
                active_admins = User.objects.filter(
                    role="admin",
                    is_active=True
                ).count()

                if active_admins <= 1:
                    raise ValidationError(
                        "You cannot remove or deactivate the last active admin."
                    )

        user = serializer.save()

        changes = []

        if old_role != user.role:
            changes.append(f"Role changed from {old_role} to {user.role}")

        if old_active != user.is_active:
            status_text = "activated" if user.is_active else "deactivated"
            changes.append(f"User account {status_text}")

        if changes:
            notify_roles(
                roles=["admin"],
                title="User Account Updated",
                message=(
                    f"Account: {user.email}. "
                    + ". ".join(changes)
                ),
                notification_type="system",
                related_url=f"/users/{user.pk}",
                exclude_users=[self.request.user],
            )


    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError("You cannot delete your own account.")

        if instance.role == "admin" and instance.is_active:
            active_admins = User.objects.filter(
                role="admin",
                is_active=True
            ).count()

            if active_admins <= 1:
                raise ValidationError(
                    "You cannot delete the last active admin."
                )

        deleted_email = instance.email
        deleted_role = instance.role
        deleted_user_id = instance.pk

        instance.delete()

        notify_roles(
            roles=["admin"],
            title="User Account Deleted",
            message=(
                f"User account {deleted_email} "
                f"(Role: {deleted_role}) has been deleted."
                f' User ID: {deleted_user_id}'
            ),
            notification_type="system",
            exclude_users=[self.request.user],
        )



