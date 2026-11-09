from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import (
    Count,
    Sum,
    F,
    Q,
    DecimalField,
    ExpressionWrapper,
)

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from notifications.services import create_notification, notify_roles
from inventory.models import StockMovement
from inventory.serializers import (
    StockMovementSerializer,
    StockAdjustmentSerializer,
)
from inventory.permissions import (
    IsAuthenticatedReadOnly,
    IsAdminOrManagerForStockAdjustment,
)
from inventory.services import adjust_stock as apply_stock_adjustment
from product.models import Product


class StockMovementViewSet(ModelViewSet):
    queryset = StockMovement.objects.select_related("product")
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticatedReadOnly]

    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "adjust_stock":
            return [IsAdminOrManagerForStockAdjustment()]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()

        product_id = self.request.query_params.get("product")
        movement_type = self.request.query_params.get("movement_type")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        search = self.request.query_params.get("search")

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search)
                | Q(product__sku__icontains=search)
                | Q(product__barcode__icontains=search)
            )

        return queryset

    @action(
    detail=False,
    methods=["post"],
    url_path="adjust-stock",
)
    def adjust_stock(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            movement = apply_stock_adjustment(
                product_id=data["product"].pk,
                movement_type=data["movement_type"],
                quantity=data["quantity"],
                note=data.get("note", ""),
            )
        except Product.DoesNotExist:
            raise NotFound("Product not found.")
        except DjangoValidationError as exc:
            raise ValidationError({"detail": exc.messages})

        product = movement.product

        action_text = (
            "increased"
            if movement.movement_type == "adjustment_in"
            else "decreased"
        )

        # Notify other Admins and Managers
        notify_roles(
            roles=["admin", "manager"],
            title="Stock Adjusted",
            message=(
                f"Stock of {product.name} has been {action_text} "
                f"by {movement.quantity}. "
                f"Current stock: {product.stock}."
            ),
            notification_type="stock_adjustment",
            exclude_users=[request.user],
        )

        # Notify the user who performed the adjustment
        create_notification(
            recipient=request.user,
            title="Stock Adjustment Successful",
            message=(
                f"You have {action_text} the stock of {product.name} "
                f"by {movement.quantity}. "
                f"Current stock: {product.stock}."
            ),
            notification_type="stock_adjustment",
        )

        return Response(
            StockMovementSerializer(movement).data,
            status=status.HTTP_201_CREATED,
        )

    

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def summary(self, request):
        products = Product.objects.all()

        stock_value_expression = ExpressionWrapper(
            F("stock") * F("cost_price"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

        summary = products.aggregate(
            total_products=Count("id"),
            total_stock_units=Sum("stock"),
            low_stock_products=Count(
                "id",
                filter=Q(
                    stock__gt=0,
                    stock__lte=F("low_stock_threshold"),
                ),
            ),
            out_of_stock_products=Count(
                "id",
                filter=Q(stock=0),
            ),
            inventory_cost_value=Sum(stock_value_expression),
        )

        return Response({
            "total_products": summary["total_products"] or 0,
            "total_stock_units": summary["total_stock_units"] or 0,
            "low_stock_products": summary["low_stock_products"] or 0,
            "out_of_stock_products": summary["out_of_stock_products"] or 0,
            "inventory_cost_value": summary["inventory_cost_value"] or 0,
        })