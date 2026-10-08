from django.db import models
from product.models import Product

# Create your models here.

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("purchase", "Purchase"),
        ("sale", "Sale"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
    ]

    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name="stock_movements")
    movement_type = models.CharField(max_length=20,choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"{self.movement_type} - {self.product.name} - {self.quantity}"
    
    
    
    