from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from rest_framework import serializers
from purchases.models import Purchase, PurchaseItem, SupplierReturn, SupplierReturnItem
from product.models import Product
from inventory.services import adjust_stock
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Sum
from product.serializers import ProductSerializer
from notifications.services import create_notification, notify_roles



class PurchaseItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False,
        allow_null=True,
    )

    new_product = ProductSerializer(
        write_only=True,
        required=False,
    )

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "product",
            "new_product",
            "quantity",
            "cost_price",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )
        return value

    def validate_cost_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Cost price cannot be negative."
            )
        return value

    def validate(self, attrs):
        product = attrs.get("product")
        new_product = attrs.get("new_product")

        if bool(product) == bool(new_product):
            raise serializers.ValidationError(
                "Provide either an existing product or a new product, not both."
            )

        return attrs

    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Purchase items cannot be edited after creation."
        )


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(
        many=True,
        source="purchase_items",
    )

    class Meta:
        model = Purchase
        fields = [
            "id",
            "supplier",
            "created_by",
            "total_amount",
            "items",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "total_amount",
            "created_at",
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one purchase item is required."
            )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("purchase_items")
        request = self.context["request"]

        purchase = Purchase.objects.create(
            created_by=request.user,
            total_amount=Decimal("0.00"),
            **validated_data,
        )

        total = Decimal("0.00")

        for item_data in items_data:
            quantity = item_data["quantity"]
            cost_price = item_data["cost_price"]

            # Create a new product or retrieve an existing one.
            new_product_data = item_data.get("new_product")

            if new_product_data:
                product = Product.objects.create(
                    **new_product_data
                )
            else:
                product = Product.objects.select_for_update().get(
                    pk=item_data["product"].pk
                )

            # Calculate weighted average cost price.
            old_stock = product.stock
            old_cost_price = product.cost_price

            new_stock = old_stock + quantity

            average_cost = (
                (old_cost_price * old_stock)
                + (cost_price * quantity)
            ) / new_stock

            product.cost_price = average_cost.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            product.save(
                update_fields=["cost_price", "updated_at"]
            )

            # Create purchase item.
            subtotal = cost_price * quantity

            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=quantity,
                cost_price=cost_price,
                subtotal=subtotal,
            )

            # Increase stock.
            adjust_stock(
                product_id=product.pk,
                movement_type="purchase",
                quantity=quantity,
                note=f"Purchase #{purchase.pk}",
            )

            total += subtotal

        purchase.total_amount = total
        purchase.save(update_fields=["total_amount"])

        # Notify Admin and Manager
        notify_roles(
            roles=["admin", "manager"],
            title="New Purchase Completed",
            message=(
                f"Purchase #{purchase.pk} has been completed. "
                f"Supplier: {purchase.supplier.name}. "
                f"Total amount: {purchase.total_amount}."
            ),
            notification_type="purchase",
            related_url=f"/purchases/{purchase.pk}",
            exclude_users=[request.user],
        )

        # Notify the user who created the purchase
        create_notification(
            recipient=request.user,
            title="Purchase Completed Successfully",
            message=(
                f"Your purchase #{purchase.pk} has been completed. "
                f"Supplier: {purchase.supplier.name}. "
                f"Total amount: {purchase.total_amount}."
            ),
            notification_type="purchase",
            related_url=f"/purchases/{purchase.pk}",
        )

        return purchase

    def update(self, instance, validated_data):
        if "purchase_items" in validated_data:
            raise serializers.ValidationError(
                "Purchase items cannot be changed after creation."
            )

        raise serializers.ValidationError(
            "Purchases cannot be edited. Create a separate purchase instead."
        )



class SupplierReturnItemInputSerializer(serializers.Serializer):
    purchase_item = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseItem.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)


class SupplierReturnSerializer(serializers.ModelSerializer):
    items = SupplierReturnItemInputSerializer(many=True)

    class Meta:
        model = SupplierReturn
        fields = [
            "id",
            "purchase",
            "created_by",
            "total_amount",
            "items",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "purchase",
            "created_by",
            "total_amount",
            "created_at",
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "At least one supplier return item is required."
            )

        purchase = self.context["purchase"]
        seen = set()

        for item in items:
            purchase_item = item["purchase_item"]
            quantity = item["quantity"]

            if purchase_item.purchase_id != purchase.pk:
                raise serializers.ValidationError(
                    "A returned item does not belong to this purchase."
                )

            if purchase_item.pk in seen:
                raise serializers.ValidationError(
                    "Do not submit the same purchase item more than once."
                )
            seen.add(purchase_item.pk)

            already_returned = (
                SupplierReturnItem.objects.filter(
                    purchase_item=purchase_item
                ).aggregate(total=Sum("quantity"))["total"]
                or 0
            )

            remaining = purchase_item.quantity - already_returned

            if quantity > remaining:
                raise serializers.ValidationError(
                    f"Purchase item #{purchase_item.pk}: "
                    f"only {remaining} unit(s) can still be returned."
                )

        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        purchase = self.context["purchase"]
        request = self.context["request"]

        supplier_return = SupplierReturn.objects.create(
            purchase=purchase,
            created_by=request.user,
            total_amount=0,
        )

        total = 0

        for item_data in items_data:
            purchase_item = PurchaseItem.objects.select_for_update().get(
                pk=item_data["purchase_item"].pk,
                purchase=purchase,
            )
            quantity = item_data["quantity"]

            already_returned = (
                SupplierReturnItem.objects.filter(
                    purchase_item=purchase_item
                ).aggregate(total=Sum("quantity"))["total"]
                or 0
            )

            remaining = purchase_item.quantity - already_returned

            if quantity > remaining:
                raise serializers.ValidationError({
                    "items": (
                        f"Purchase item #{purchase_item.pk} has only "
                        f"{remaining} unit(s) remaining for return."
                    )
                })

            subtotal = purchase_item.cost_price * quantity

            SupplierReturnItem.objects.create(
                supplier_return=supplier_return,
                purchase_item=purchase_item,
                quantity=quantity,
                cost_price=purchase_item.cost_price,
                subtotal=subtotal,
            )

            try:
                adjust_stock(
                    product_id=purchase_item.product_id,
                    movement_type="supplier_return",
                    quantity=quantity,
                    note=(
                        f"Supplier return #{supplier_return.pk}, "
                        f"purchase #{purchase.pk}"
                    ),
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError({
                    "items": exc.messages
                }) from exc

            total += subtotal

        supplier_return.total_amount = total
        supplier_return.save(update_fields=["total_amount"])

        # Notify Admin and Manager
        notify_roles(
            roles=["admin", "manager"],
            title="Supplier Return Completed",
            message=(
                f"Supplier return #{supplier_return.pk} has been completed. "
                f"Purchase #{purchase.pk}, "
                f"Supplier: {purchase.supplier.name}. "
                f"Total amount: {supplier_return.total_amount}."
            ),
            notification_type="supplier_return",
            related_url=f"/purchases/{purchase.pk}",
            exclude_users=[request.user],
        )

        # Notify the user who created the supplier return
        create_notification(
            recipient=request.user,
            title="Supplier Return Completed Successfully",
            message=(
                f"Your supplier return #{supplier_return.pk} "
                f"for Purchase #{purchase.pk} has been completed. "
                f"Total amount: {supplier_return.total_amount}."
            ),
            notification_type="supplier_return",
            related_url=f"/purchases/{purchase.pk}",
        )

        return supplier_return

    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Supplier returns cannot be edited. Create a separate return "
            "record if another return is needed."
        )


