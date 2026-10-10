from rest_framework.viewsets import ModelViewSet
from customers.models import Customer
from customers.serializers import CustomerSerializer
from users.permissions import IsAdminManagerOrCashierForCustomer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminManagerOrCashierForCustomer]
