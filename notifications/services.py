from notifications.models import Notification


def create_notification(recipient,title,message,notification_type="system",related_url=None,):
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_url=related_url,
    )


def notify_roles(roles,title,message,notification_type="system",related_url=None,exclude_users=None,):
    from users.models import User

    recipients = User.objects.filter(
        role__in=roles,
        is_active=True,
    )

    if exclude_users:
        recipients = recipients.exclude(
            pk__in=[user.pk for user in exclude_users]
        )

    notifications = [
        Notification(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
            related_url=related_url,
        )
        for user in recipients
    ]

    return Notification.objects.bulk_create(notifications)

