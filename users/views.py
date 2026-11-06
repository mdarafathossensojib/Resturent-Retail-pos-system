from rest_framework.viewsets import ModelViewSet
from users.models import User
from users.serializers import UserCRUDSerializer
from users.permissions import IsAdmin
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


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

    def perform_update(self, serializer):
        user = self.get_object()

        new_role = serializer.validated_data.get("role", user.role)
        new_active = serializer.validated_data.get("is_active", user.is_active)

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

        serializer.save()

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

        instance.delete()


