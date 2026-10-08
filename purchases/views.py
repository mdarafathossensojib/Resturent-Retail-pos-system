from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from purchases.models import Purchase, PurchaseItem
from purchases.serializers import PurchaseItemSerializer, PurchaseSerializer


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.select_related('supplier', 'created_by')
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]


class PurchaseItemViewSet(ModelViewSet):
    queryset = PurchaseItem.objects.select_related('purchase', 'product')
    serializer_class = PurchaseItemSerializer
    permission_classes = [IsAuthenticated]
