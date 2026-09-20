from django.db import models
from users.models import User
from suppliers.models import Supplier
from product.models import Product

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
    
    
    