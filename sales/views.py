from rest_framework.viewsets import ModelViewSet
from sales.models import Sale, SaleItem
from sales.serializers import SaleSerializer, SaleItemSerializer
from sales.permissions import IsAdminManagerOrCashierForSales
from purchases.permissions import IsAuthenticatedReadOnly, IsAdminOrManager
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from inventory.services import adjust_stock


class SaleViewSet(ModelViewSet):
    queryset = Sale.objects.select_related(
        "customer", "cashier"
    ).prefetch_related("items__product")

    serializer_class = SaleSerializer
    permission_classes = [IsAdminManagerOrCashierForSales]

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
            raise ValidationError(
                {"detail": "Only completed sales can be refunded."}
            )

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
                raise ValidationError({"detail": exc.messages}) from exc

        sale.status = "refunded"
        sale.save(update_fields=["status"])

        return Response(
            self.get_serializer(sale).data,
            status=status.HTTP_200_OK,
        )
    
    http_method_names = ["get", "post", "head", "options"]


class SaleItemViewSet(ModelViewSet):
    queryset = SaleItem.objects.select_related(
        "sale", "product"
    )

    serializer_class = SaleItemSerializer
    permission_classes = [IsAuthenticatedReadOnly]
    http_method_names = ["get", "head", "options"]
