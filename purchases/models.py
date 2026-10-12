from django.db import models
from users.models import User
from suppliers.models import Supplier
from product.models import Product
from django.conf import settings
from django.core.validators import MinValueValidator

# Create your models here.

class Purchase(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases"
    )

    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    total_amount = models.DecimalField(max_digits=12,decimal_places=2)

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"Purchase from {self.supplier.name} - {self.total_amount}"
    
    
class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="purchase_items"
    )

    product = models.ForeignKey(Product,on_delete=models.PROTECT, related_name="purchase_items")
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10,decimal_places=2)
    subtotal = models.DecimalField(max_digits=12,decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} - {self.subtotal}"
    

class SupplierReturn(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.PROTECT,
        related_name="supplier_returns",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_returns",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Supplier Return #{self.pk} - Purchase #{self.purchase_id}"


class SupplierReturnItem(models.Model):
    supplier_return = models.ForeignKey(
        SupplierReturn,
        on_delete=models.CASCADE,
        related_name="items",
    )
    purchase_item = models.ForeignKey(
        PurchaseItem,
        on_delete=models.PROTECT,
        related_name="supplier_return_items",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="supplier_return_item_quantity_gt_zero",
            ),
        ]

    def __str__(self):
        return (
            f"Purchase Item #{self.purchase_item_id} "
            f"- Return Qty: {self.quantity}"
        )