import re

from bot.config import SUPPORTED_ORDER_TYPES, SUPPORTED_SIDES
from bot.exceptions import ValidationError


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValidationError("Symbol is required")
    if not re.match(r"^[A-Z0-9]{2,20}$", symbol):
        raise ValidationError(f"Invalid symbol format: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in SUPPORTED_SIDES:
        raise ValidationError(
            f"Invalid side: {side}. Must be one of: {', '.join(SUPPORTED_SIDES)}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in SUPPORTED_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type: {order_type}. Must be one of: {', '.join(SUPPORTED_ORDER_TYPES)}"
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    if quantity is None:
        raise ValidationError("Quantity is required")
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity: {quantity}. Must be a number")
    if quantity <= 0:
        raise ValidationError(f"Quantity must be positive, got: {quantity}")
    return quantity


def validate_price(price: float | None, order_type: str) -> float | None:
    if order_type in ("LIMIT", "STOP"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid price: {price}. Must be a number")
        if price <= 0:
            raise ValidationError(f"Price must be positive, got: {price}")
        return price
    return None


def validate_stop_price(stop_price: float | None, order_type: str) -> float | None:
    if order_type in ("STOP_MARKET", "STOP"):
        if stop_price is None:
            raise ValidationError(f"Stop price is required for {order_type} orders")
        try:
            stop_price = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid stop price: {stop_price}. Must be a number")
        if stop_price <= 0:
            raise ValidationError(f"Stop price must be positive, got: {stop_price}")
        return stop_price
    return None


def validate_grid_params(
    lower_price: float, upper_price: float, grid_levels: int
) -> tuple[float, float, int]:
    if lower_price is None or upper_price is None or grid_levels is None:
        raise ValidationError("Grid requires lower_price, upper_price, and grid_levels")
    try:
        lower_price = float(lower_price)
        upper_price = float(upper_price)
        grid_levels = int(grid_levels)
    except (TypeError, ValueError):
        raise ValidationError("Grid parameters must be valid numbers")
    if lower_price <= 0 or upper_price <= 0:
        raise ValidationError("Grid prices must be positive")
    if lower_price >= upper_price:
        raise ValidationError("Lower price must be less than upper price")
    if grid_levels < 2 or grid_levels > 50:
        raise ValidationError("Grid levels must be between 2 and 50")
    return lower_price, upper_price, grid_levels


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> dict:
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type.strip().upper()),
        "stop_price": validate_stop_price(stop_price, order_type.strip().upper()),
    }
