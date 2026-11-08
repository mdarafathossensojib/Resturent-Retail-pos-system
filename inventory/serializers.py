from rest_framework import serializers
from inventory.models import StockMovement
from product.models import Product

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "movement_type",
            "quantity",
            "note",
            "created_at",
        ]
        read_only_fields = fields

class StockAdjustmentSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    movement_type = serializers.ChoiceField(
        choices=[
            ("adjustment_in", "Adjustment In"),
            ("adjustment_out", "Adjustment Out"),
        ]
    )

    quantity = serializers.IntegerField(min_value=1)

    note = serializers.CharField(
        required=False,
        allow_blank=True
    )