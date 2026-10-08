from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from sales.models import Sale, SaleItem
from sales.serializers import SaleItemSerializer, SaleSerializer


class SaleViewSet(ModelViewSet):
    queryset = Sale.objects.select_related('customer', 'cashier')
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]


class SaleItemViewSet(ModelViewSet):
    queryset = SaleItem.objects.select_related('sale', 'product')
    serializer_class = SaleItemSerializer
    permission_classes = [IsAuthenticated]
