from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from suppliers.models import Supplier
from suppliers.serializers import SupplierSerializer


class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
