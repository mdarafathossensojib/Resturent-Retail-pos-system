from django.contrib import admin
from purchases.models import Purchase, PurchaseItem

# Register your models here.

admin.site.register(Purchase)
admin.site.register(PurchaseItem)