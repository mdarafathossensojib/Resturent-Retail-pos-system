import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from inventory.services import adjust_stock
from sales.models import Sale, SaleItem
from product.models import Product


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            "id",
            "product",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["id", "unit_price", "subtotal"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )
        return value


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "invoice_number",
            "customer",
            "cashier",
            "items",
            "total_amount",
            "discount_amount",
            "tax_amount",
            "final_amount",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "cashier",
            "total_amount",
            "final_amount",
            "status",
            "created_at",
        ]

    def validate_discount_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Discount cannot be negative."
            )
        return value

    def validate_tax_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Tax cannot be negative."
            )
        return value

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one sale item is required."
            )
        return items

    def validate(self, attrs):
        if self.instance is not None:
            raise serializers.ValidationError(
                "Existing sales cannot be edited."
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context["request"]

        discount = validated_data.get(
            "discount_amount", Decimal("0.00")
        )
        tax = validated_data.get(
            "tax_amount", Decimal("0.00")
        )

        total = Decimal("0.00")

        # Lock products and calculate prices on the server.
        prepared_items = []

        for item_data in items_data:
            product = Product.objects.select_for_update().get(
                pk=item_data["product"].pk
            )

            quantity = item_data["quantity"]
            unit_price = product.selling_price
            subtotal = unit_price * quantity

            prepared_items.append(
                (product, quantity, unit_price, subtotal)
            )
            total += subtotal

        final_amount = total - discount + tax

        if final_amount < 0:
            raise serializers.ValidationError({
                "discount_amount":
                    "Discount cannot exceed total amount plus tax."
            })

        sale = Sale.objects.create(
            invoice_number=f"INV-{uuid.uuid4().hex[:12].upper()}",
            cashier=request.user,
            total_amount=total,
            discount_amount=discount,
            tax_amount=tax,
            final_amount=final_amount,
            **validated_data,
        )

        for product, quantity, unit_price, subtotal in prepared_items:
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )

            try:
                adjust_stock(
                    product_id=product.pk,
                    movement_type="sale",
                    quantity=quantity,
                    note=f"Sale invoice {sale.invoice_number}",
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError({
                    "items": exc.messages
                }) from exc

        return sale

    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Sales cannot be edited. Use a dedicated refund workflow."
        )

