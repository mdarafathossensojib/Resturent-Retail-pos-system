from django.db import models
from users.models import User
from customers.models import Customer
from product.models import Product

# Create your models here.

class Sale(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("refunded", "Refunded"),
    ]

    invoice_number = models.CharField(max_length=30,unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cashier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    total_amount = models.DecimalField(max_digits=12,decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    tax_amount = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    final_amount = models.DecimalField(max_digits=12,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="completed")

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"Sale {self.invoice_number} - {self.customer} - {self.final_amount}"

class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    subtotal = models.DecimalField(max_digits=12,decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.unit_price} = {self.subtotal}"


