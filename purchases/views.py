from rest_framework.viewsets import ModelViewSet
from purchases.models import Purchase, PurchaseItem
from purchases.serializers import PurchaseSerializer, PurchaseItemSerializer
from purchases.permissions import IsAdminOrManager, IsAuthenticatedReadOnly


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.select_related(
        "supplier", "created_by"
    ).prefetch_related("purchase_items__product")

    serializer_class = PurchaseSerializer
    permission_classes = [IsAdminOrManager]
    http_method_names = ["get", "post", "head", "options"]


class PurchaseItemViewSet(ModelViewSet):
    queryset = PurchaseItem.objects.select_related(
        "purchase", "product"
    )

    serializer_class = PurchaseItemSerializer
    permission_classes = [IsAuthenticatedReadOnly]
    http_method_names = ["get", "head", "options"]
