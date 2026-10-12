from django.core.validators import MinValueValidator
from django.db import models
from sales.models import Sale
from django.conf import settings


class Payment(models.Model):
    METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile_banking", "Mobile Banking"),
    ]

    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    method = models.CharField(max_length=30, choices=METHODS)

    # This payment's actual contribution to the sale
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    # Amount physically received from the customer
    amount_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
    )

    # Change returned to the customer
    change_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="payment_amount_gt_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(change_amount__gte=0),
                name="payment_change_nonnegative",
            ),
        ]

    def __str__(self):
        return (
            f"Payment for Sale {self.sale.invoice_number} "
            f"- {self.method} - {self.amount}"
        )
    


class SaleRefund(models.Model):
    REFUND_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile_banking", "Mobile Banking"),
        ("mixed", "Multiple Methods"),
        ("none", "No Payment Collected"),
    ]

    sale = models.OneToOneField(
        "sales.Sale",
        on_delete=models.PROTECT,
        related_name="refund_record",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    method = models.CharField(
        max_length=30,
        choices=REFUND_METHODS,
        default="none",
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    refunded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sale_refunds",
    )
    refunded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-refunded_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="sale_refund_amount_nonnegative",
            ),
        ]

    def __str__(self):
        return (
            f"Refund for Sale {self.sale.invoice_number} "
            f"- {self.amount}"
        )