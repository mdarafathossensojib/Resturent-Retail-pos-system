from rest_framework.viewsets import ModelViewSet
from inventory.models import StockMovement
from inventory.serializers import StockMovementSerializer
from inventory.permissions import IsAuthenticatedReadOnly


class StockMovementViewSet(ModelViewSet):
    queryset = StockMovement.objects.select_related("product")
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticatedReadOnly]
    http_method_names = ["get", "head", "options"]
