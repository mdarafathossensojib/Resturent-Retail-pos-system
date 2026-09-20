from django.db import models
from sales.models import Sale

# Create your models here.

class Payment(models.Model):
    METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile_banking", "Mobile Banking"),
    ]

    sale = models.OneToOneField(Sale,on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=30,choices=METHODS)
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    transaction_id = models.CharField(max_length=100,blank=True)

    paid_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f"Payment for Sale {self.sale.invoice_number} - {self.method} - {self.amount}"
    
    
    