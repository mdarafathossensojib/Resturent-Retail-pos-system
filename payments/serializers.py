from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from payments.models import Payment, SaleRefund
from sales.models import Sale


class PaymentSerializer(serializers.ModelSerializer):
    amount_received = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        required=True,
    )
    class Meta:
        model = Payment
        fields = [
            "id",
            "sale",
            "method",
            "amount",
            "amount_received",
            "change_amount",
            "transaction_id",
            "paid_at",
        ]
        read_only_fields = [
            "id",
            "amount",
            "change_amount",
            "paid_at",
        ]

    def validate_amount_received(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount received must be greater than zero."
            )
        return value

    def validate(self, attrs):
        if self.instance is not None:
            raise serializers.ValidationError(
                "Payments cannot be edited."
            )

        sale = attrs.get("sale")

        if sale and sale.status != "completed":
            raise serializers.ValidationError({
                "sale": "Payment is allowed only for completed sales."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        sale_id = validated_data["sale"].pk
        sale = Sale.objects.select_for_update().get(pk=sale_id)

        if sale.status != "completed":
            raise serializers.ValidationError({
                "sale": "Payment is allowed only for completed sales."
            })

        paid_total = (
            Payment.objects.filter(sale=sale)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        remaining = sale.final_amount - paid_total

        if remaining <= 0:
            raise serializers.ValidationError({
                "sale": "This sale is already fully paid."
            })

        received = validated_data["amount_received"]
        method = validated_data["method"]

        if method == "cash":
            amount = min(received, remaining)
            change = max(received - remaining, Decimal("0.00"))
        else:
            if received > remaining:
                raise serializers.ValidationError({
                    "amount_received": (
                        f"Remaining payable amount is {remaining}. "
                        "Card/mobile payment cannot exceed this amount."
                    )
                })

            amount = received
            change = Decimal("0.00")

        validated_data["sale"] = sale
        validated_data["amount"] = amount
        validated_data["change_amount"] = change

        return Payment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Payments cannot be edited."
        )



class SaleRefundSerializer(serializers.ModelSerializer):
    sale_invoice = serializers.CharField(
        source="sale.invoice_number",
        read_only=True,
    )
    refunded_by_email = serializers.EmailField(
        source="refunded_by.email",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = SaleRefund
        fields = [
            "id",
            "sale",
            "sale_invoice",
            "amount",
            "method",
            "transaction_id",
            "note",
            "refunded_by",
            "refunded_by_email",
            "refunded_at",
        ]
        read_only_fields = fields
