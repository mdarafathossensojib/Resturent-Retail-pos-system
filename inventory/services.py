from django.core.exceptions import ValidationError
from django.db import transaction
from inventory.models import StockMovement
from product.models import Product
from notifications.services import notify_roles


INCREASE_TYPES = {"purchase", "return", "adjustment_in"}
DECREASE_TYPES = {"sale", "adjustment_out", "supplier_return"}

VALID_MOVEMENT_TYPES = INCREASE_TYPES | DECREASE_TYPES


@transaction.atomic
def adjust_stock(product_id, movement_type, quantity, note=""):
    if movement_type not in VALID_MOVEMENT_TYPES:
        raise ValidationError("Invalid stock movement type.")

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValidationError("Quantity must be a positive integer.")

    product = Product.objects.select_for_update().get(pk=product_id)

    if movement_type in DECREASE_TYPES and product.stock < quantity:
        raise ValidationError(
            f"Insufficient stock for {product.name}. "
            f"Available: {product.stock}, requested: {quantity}."
        )

    previous_stock = product.stock

    if movement_type in INCREASE_TYPES:
        product.stock += quantity
    else:
        product.stock -= quantity

    product.save(update_fields=["stock", "updated_at"])

    movement = StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
    )

    # Notify Admin and Manager when stock crosses the low-stock threshold.
    if(previous_stock > product.low_stock_threshold and product.stock <= product.low_stock_threshold):
        notify_roles(
            roles=["admin", "manager"],
            title="Low Stock Alert",
            message=(
                f"{product.name} is running low on stock. "
                f"Current stock: {product.stock}, "
                f"threshold: {product.low_stock_threshold}."
            ),
            notification_type="low_stock",
        )

    return movement


