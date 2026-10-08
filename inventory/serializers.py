from rest_framework import serializers

from inventory.models import StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            'id',
            'product',
            'movement_type',
            'quantity',
            'note',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
