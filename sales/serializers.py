from rest_framework import serializers

from sales.models import Sale, SaleItem


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id',
            'invoice_number',
            'customer',
            'cashier',
            'total_amount',
            'discount_amount',
            'tax_amount',
            'final_amount',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id', 'sale', 'product', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id']
