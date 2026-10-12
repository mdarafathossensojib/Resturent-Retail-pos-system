from django.core.exceptions import ValidationError
from django.db import transaction
from inventory.models import StockMovement
from product.models import Product


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

    return movement
