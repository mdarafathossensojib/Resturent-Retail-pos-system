from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from customers.models import Customer
from customers.serializers import CustomerSerializer
from customers.permissions import IsAdminManagerOrCashierForCustomer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all().order_by("-created_at")
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminManagerOrCashierForCustomer]

    @action(detail=False, methods=["get"], url_path="lookup")
    def lookup(self, request):
        phone = request.query_params.get("phone", "").strip()

        if not phone:
            raise ValidationError({
                "phone": "Customer phone number is required."
            })

        customer = Customer.objects.filter(phone=phone).first()

        if customer is None:
            return Response({
                "found": False,
                "detail": "Customer not found.",
            }, status=status.HTTP_200_OK)

        return Response({
            "found": True,
            "customer": self.get_serializer(customer).data,
        }, status=status.HTTP_200_OK)
