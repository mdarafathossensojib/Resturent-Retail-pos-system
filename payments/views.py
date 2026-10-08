from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.select_related('sale')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
