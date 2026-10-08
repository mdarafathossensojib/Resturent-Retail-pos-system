from rest_framework import serializers

from purchases.models import Purchase, PurchaseItem


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'supplier', 'created_by', 'total_amount', 'created_at']
        read_only_fields = ['id', 'created_at']


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['id', 'purchase', 'product', 'quantity', 'cost_price', 'subtotal']
        read_only_fields = ['id']
