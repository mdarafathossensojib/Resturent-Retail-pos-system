from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'sale',
            'method',
            'amount',
            'transaction_id',
            'paid_at',
        ]
        read_only_fields = ['id', 'paid_at']
