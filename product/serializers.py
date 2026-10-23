from rest_framework import serializers

from product.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count']
        read_only_fields = ['id', "product_count"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'name',
            'sku',
            'barcode',
            'cost_price',
            'selling_price',
            'stock',
            'low_stock_threshold',
            'image',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'stock', 'created_at', 'updated_at']
