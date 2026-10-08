from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from inventory.models import StockMovement
from inventory.serializers import StockMovementSerializer


class StockMovementViewSet(ModelViewSet):
    queryset = StockMovement.objects.select_related('product')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
