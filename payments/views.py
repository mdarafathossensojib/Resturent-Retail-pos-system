from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from payments.models import Payment, SaleRefund
from payments.serializers import PaymentSerializer, SaleRefundSerializer
from payments.permissions import IsAdminManagerOrCashierForPayments
from sales.models import Sale
from django.db.models import Sum
from decimal import Decimal
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.select_related(
        "sale",
        "sale__customer",
        "sale__cashier",
    )
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminManagerOrCashierForPayments]
    http_method_names = ["get", "post", "head", "options"]

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")

    @action(detail=False, methods=["get"], url_path="due")
    def due(self, request):
        sale_id = request.query_params.get("sale_id")

        if not sale_id:
            raise ValidationError({
                "sale_id": "This query parameter is required."
            })

        sale = get_object_or_404(Sale, pk=sale_id)

        paid_total = (
            Payment.objects.filter(sale=sale)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        remaining = max(
            sale.final_amount - paid_total,
            Decimal("0.00"),
        )

        return Response({
            "sale_id": sale.pk,
            "invoice_number": sale.invoice_number,
            "status": sale.status,
            "final_amount": sale.final_amount,
            "paid_total": paid_total,
            "remaining_due": remaining,
            "can_accept_payment": (
                sale.status == "completed" and remaining > 0
            ),
        }, status=status.HTTP_200_OK)
    


class SaleRefundViewSet(ReadOnlyModelViewSet):
    queryset = SaleRefund.objects.select_related(
        "sale", "refunded_by"
    )
    serializer_class = SaleRefundSerializer
    permission_classes = [IsAdminManagerOrCashierForPayments]
    http_method_names = ["get", "head", "options"]


