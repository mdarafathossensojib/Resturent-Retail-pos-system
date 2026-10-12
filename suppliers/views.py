from rest_framework.viewsets import ModelViewSet
from suppliers.models import Supplier
from suppliers.serializers import SupplierSerializer
from product.permissions import IsAdminOrManagerOrReadOnly

class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]
