from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        SALE = "sale", "Sale"
        PURCHASE = "purchase", "Purchase"
        REFUND = "refund", "Refund"
        SUPPLIER_RETURN = "supplier_return", "Supplier Return"
        LOW_STOCK = "low_stock", "Low Stock"
        STOCK_ADJUSTMENT = "stock_adjustment", "Stock Adjustment"
        PAYMENT = "payment", "Payment"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )

    related_url = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient}"
