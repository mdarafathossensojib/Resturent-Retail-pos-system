from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50,unique=True)
    barcode = models.CharField(max_length=100,unique=True,blank=True,null=True)
    cost_price = models.DecimalField(max_digits=10,decimal_places=2)
    selling_price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    image = CloudinaryField('Products', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
    