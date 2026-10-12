from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from sales.models import Sale, SaleItem
from payments.models import SaleRefund, Payment
from payments.serializers import SaleRefundSerializer
from sales.serializers import SaleSerializer, SaleItemSerializer
from sales.permissions import IsAdminManagerOrCashierForSales
from purchases.permissions import IsAuthenticatedReadOnly, IsAdminOrManager
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from inventory.services import adjust_stock
from django.db.models import Sum
from decimal import Decimal


class SaleViewSet(ModelViewSet):
    queryset = Sale.objects.select_related(
        "customer", "cashier"
    ).prefetch_related("items__product")

    serializer_class = SaleSerializer
    permission_classes = [IsAdminManagerOrCashierForSales]
    http_method_names = ["get", "post", "head", "options"]

    
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrManager],
        url_path="refund",
    )
    @transaction.atomic
    def refund(self, request, pk=None):
        sale = get_object_or_404(
            Sale.objects.select_for_update(),
            pk=pk,
        )

        self.check_object_permissions(request, sale)

        if sale.status != "completed":
            raise ValidationError({
                "detail": "Only completed sales can be refunded."
            })

        if SaleRefund.objects.filter(sale=sale).exists():
            raise ValidationError({
                "detail": "This sale has already been refunded."
            })

        # Validate refund metadata before changing stock.
        class RefundRequestSerializer(serializers.Serializer):
            method = serializers.ChoiceField(
                choices=["cash", "card", "mobile_banking", "mixed"],
                required=False,
            )
            transaction_id = serializers.CharField(
                max_length=100,
                required=False,
                allow_blank=True,
                default="",
            )
            note = serializers.CharField(
                required=False,
                allow_blank=True,
                default="",
            )

        request_serializer = RefundRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        refund_data = request_serializer.validated_data

        paid_total = (
            Payment.objects.filter(sale=sale)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        if paid_total > 0 and "method" not in refund_data:
            raise ValidationError({
                "method": "Select how the customer will receive the refund."
            })

        refund_method = (
            refund_data.get("method", "none")
            if paid_total > 0
            else "none"
        )

        # Restore all sold products to stock.
        items = sale.items.select_related("product").all()

        for item in items:
            try:
                adjust_stock(
                    product_id=item.product_id,
                    movement_type="return",
                    quantity=item.quantity,
                    note=f"Refund for invoice {sale.invoice_number}",
                )
            except DjangoValidationError as exc:
                raise ValidationError({
                    "detail": exc.messages
                }) from exc

        # Record the financial refund.
        refund = SaleRefund.objects.create(
            sale=sale,
            amount=paid_total,
            method=refund_method,
            transaction_id=refund_data.get("transaction_id", ""),
            note=refund_data.get("note", ""),
            refunded_by=request.user,
        )

        sale.status = "refunded"
        sale.save(update_fields=["status"])

        return Response(
            {
                "detail": "Sale refunded successfully.",
                "sale": self.get_serializer(sale).data,
                "refund": SaleRefundSerializer(refund).data,
            },
            status=status.HTTP_200_OK,
        )

    


class SaleItemViewSet(ModelViewSet):
    queryset = SaleItem.objects.select_related(
        "sale", "product"
    )

    serializer_class = SaleItemSerializer
    permission_classes = [IsAuthenticatedReadOnly]
    http_method_names = ["get", "head", "options"]
