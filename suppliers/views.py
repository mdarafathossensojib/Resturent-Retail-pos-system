
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from suppliers.models import Supplier
from suppliers.serializers import SupplierSerializer
from product.permissions import IsAdminOrManagerOrReadOnly


class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]

    @action(detail=False, methods=["get"], url_path="lookup")
    def lookup(self, request):
        phone = request.query_params.get("phone", "").strip()

        if not phone:
            raise ValidationError({
                "phone": "Supplier phone number is required."
            })

        suppliers = Supplier.objects.filter(phone=phone)

        if not suppliers.exists():
            return Response({
                "found": False,
                "detail": "Supplier not found.",
            }, status=status.HTTP_200_OK)

        if suppliers.count() > 1:
            raise ValidationError({
                "phone": (
                    "Multiple suppliers have this phone number. "
                    "Please resolve the duplicate supplier records."
                )
            })

        return Response({
            "found": True,
            "supplier": SupplierSerializer(
                suppliers.first(),
                context=self.get_serializer_context(),
            ).data,
        }, status=status.HTTP_200_OK)
