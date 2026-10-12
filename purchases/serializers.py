from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from purchases.models import Purchase, PurchaseItem
from inventory.services import adjust_stock


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "product",
            "quantity",
            "cost_price",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )
        return value

    def validate_cost_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Cost price cannot be negative."
            )
        return value


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(
        many=True,
        source="purchase_items",
        write_only=False,
    )

    class Meta:
        model = Purchase
        fields = [
            "id",
            "supplier",
            "created_by",
            "total_amount",
            "items",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "total_amount",
            "created_at",
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one purchase item is required."
            )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("purchase_items")
        request = self.context["request"]

        purchase = Purchase.objects.create(
            created_by=request.user,
            total_amount=Decimal("0.00"),
            **validated_data,
        )

        total = Decimal("0.00")

        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            cost_price = item_data["cost_price"]
            subtotal = cost_price * quantity

            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=quantity,
                cost_price=cost_price,
                subtotal=subtotal,
            )

            adjust_stock(
                product_id=product.pk,
                movement_type="purchase",
                quantity=quantity,
                note=f"Purchase #{purchase.pk}",
            )

            total += subtotal

        purchase.total_amount = total
        purchase.save(update_fields=["total_amount"])

        return purchase

    def update(self, instance, validated_data):
        if "purchase_items" in validated_data:
            raise serializers.ValidationError(
                "Purchase items cannot be changed after creation."
            )
        raise serializers.ValidationError(
            "Purchases cannot be edited. Create a separate purchase instead."
        )


