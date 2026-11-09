from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from notifications.pagination import NotificationPagination
from rest_framework.exceptions import ValidationError


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        queryset = Notification.objects.filter(
            recipient=self.request.user
        )

        is_read = self.request.query_params.get("is_read")

        if is_read is not None:
            if is_read.lower() not in ["true", "false"]:
                raise ValidationError({
                    "is_read": "Use true or false."
                })

            queryset = queryset.filter(
                is_read=is_read.lower() == "true"
            )

        return queryset.order_by("-created_at", "-id")


    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()

        return Response({
            "unread_count": count
        })

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        return Response({
            "message": "Notification marked as read."
        })

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        updated_count = self.get_queryset().filter(
            is_read=False
        ).update(is_read=True)

        return Response({
            "message": "All notifications marked as read.",
            "updated_count": updated_count
        })
