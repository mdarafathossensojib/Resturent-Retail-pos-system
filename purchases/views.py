from rest_framework.viewsets import ModelViewSet
from purchases.models import Purchase, PurchaseItem
from purchases.serializers import PurchaseSerializer, PurchaseItemSerializer, SupplierReturnSerializer
from purchases.permissions import IsAdminOrManager, IsAuthenticatedReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from django.shortcuts import get_object_or_404
from django.db import transaction


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.select_related(
        "supplier", "created_by"
    ).prefetch_related("purchase_items__product")

    serializer_class = PurchaseSerializer
    permission_classes = [IsAdminOrManager]
    http_method_names = ["get", "post", "head", "options"]

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrManager],
        url_path="supplier-return",
    )
    @transaction.atomic
    def supplier_return(self, request, pk=None):
        purchase = get_object_or_404(
            Purchase.objects.select_for_update(),
            pk=pk,
        )

        self.check_object_permissions(request, purchase)

        serializer = SupplierReturnSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                "purchase": purchase,
            },
        )
        serializer.is_valid(raise_exception=True)
        supplier_return = serializer.save()

        return Response(
            SupplierReturnSerializer(
                supplier_return,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseItemViewSet(ModelViewSet):
    queryset = PurchaseItem.objects.select_related(
        "purchase", "product"
    )

    serializer_class = PurchaseItemSerializer
    permission_classes = [IsAuthenticatedReadOnly]
    http_method_names = ["get", "head", "options"]
