from rest_framework import serializers


class ReportFilterSerializer(serializers.Serializer):
    period = serializers.ChoiceField(
        choices=["daily", "weekly", "monthly", "yearly"],
        default="monthly",
        required=False,
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if bool(start_date) != bool(end_date):
            raise serializers.ValidationError(
                "start_date and end_date must be provided together."
            )

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "start_date cannot be later than end_date."
            )

        return attrs


class SalesTrendSerializer(serializers.Serializer):
    period_start = serializers.DateTimeField()
    invoice_count = serializers.IntegerField()
    sales_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2
    )


class ProductPerformanceSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    sku = serializers.CharField()
    category_name = serializers.CharField(allow_null=True)
    quantity_sold = serializers.IntegerField()
    sales_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2
    )
    invoice_count = serializers.IntegerField()


class InventoryReportSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    sku = serializers.CharField()
    category_name = serializers.CharField(allow_null=True)
    stock = serializers.IntegerField()
    low_stock_threshold = serializers.IntegerField()
    cost_price = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )
    selling_price = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )
    stock_status = serializers.CharField()


class PaymentMethodReportSerializer(serializers.Serializer):
    method = serializers.CharField()
    payment_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2
    )