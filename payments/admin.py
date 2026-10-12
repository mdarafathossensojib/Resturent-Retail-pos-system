from django.contrib import admin
from payments.models import Payment, SaleRefund

# Register your models here.

admin.site.register(Payment)
admin.site.register(SaleRefund)