import logging
from typing import Any

from bot.client import BinanceClient
from bot.config import DEFAULT_TIME_IN_FORCE
from bot.models import OrderRequest, OrderResult, GridOrderConfig
from bot.validators import validate_order_params, validate_grid_params

logger = logging.getLogger("bot.orders")


class OrderService:
    def __init__(self, client: BinanceClient):
        self._client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = DEFAULT_TIME_IN_FORCE,
    ) -> OrderResult:
        validated = validate_order_params(
            symbol, side, order_type, quantity, price, stop_price
        )

        params: dict[str, Any] = {
            "symbol": validated["symbol"],
            "side": validated["side"],
            "type": validated["order_type"],
            "quantity": str(validated["quantity"]),
        }

        if validated["order_type"] in ("LIMIT", "STOP"):
            params["price"] = str(validated["price"])
            params["timeInForce"] = time_in_force

        if validated["order_type"] in ("STOP_MARKET", "STOP"):
            params["stopPrice"] = str(validated["stop_price"])

        logger.info(
            "Placing %s %s order: %s %s @ %s",
            validated["side"],
            validated["order_type"],
            validated["quantity"],
            validated["symbol"],
            validated.get("price") or "MARKET",
        )

        response = self._client.place_order(params)
        result = OrderResult.from_api_response(response)

        logger.info(
            "Order placed: id=%s status=%s executed=%s",
            result.order_id,
            result.status,
            result.executed_qty,
        )

        return result

    def place_grid_orders(
        self,
        symbol: str,
        side: str,
        quantity_per_order: float,
        lower_price: float,
        upper_price: float,
        grid_levels: int,
        time_in_force: str = DEFAULT_TIME_IN_FORCE,
    ) -> list[OrderResult]:
        lower_price, upper_price, grid_levels = validate_grid_params(
            lower_price, upper_price, grid_levels
        )

        price_step = (upper_price - lower_price) / (grid_levels - 1)
        prices = [round(lower_price + i * price_step, 2) for i in range(grid_levels)]

        logger.info(
            "Placing grid: %s %s | %d levels from %.2f to %.2f | qty=%.4f each",
            side,
            symbol,
            grid_levels,
            lower_price,
            upper_price,
            quantity_per_order,
        )

        results: list[OrderResult] = []
        for i, grid_price in enumerate(prices):
            logger.info("Grid order %d/%d @ %.2f", i + 1, grid_levels, grid_price)
            result = self.place_order(
                symbol=symbol,
                side=side,
                order_type="LIMIT",
                quantity=quantity_per_order,
                price=grid_price,
                time_in_force=time_in_force,
            )
            results.append(result)

        logger.info("Grid complete: %d/%d orders placed", len(results), grid_levels)
        return results

    @staticmethod
    def format_request_summary(request: OrderRequest) -> str:
        lines = [
            f"  Symbol:     {request.symbol}",
            f"  Side:       {request.side}",
            f"  Type:       {request.order_type}",
            f"  Quantity:   {request.quantity}",
        ]
        if request.price is not None:
            lines.append(f"  Price:      {request.price}")
        if request.stop_price is not None:
            lines.append(f"  Stop Price: {request.stop_price}")
        lines.append(f"  TIF:        {request.time_in_force}")
        return "\n".join(lines)

    @staticmethod
    def format_result_summary(result: OrderResult) -> str:
        lines = [
            f"  Order ID:     {result.order_id}",
            f"  Symbol:       {result.symbol}",
            f"  Side:         {result.side}",
            f"  Type:         {result.order_type}",
            f"  Status:       {result.status}",
            f"  Orig Qty:     {result.orig_qty}",
            f"  Executed Qty: {result.executed_qty}",
            f"  Avg Price:    {result.avg_price}",
        ]
        if result.price and result.price != "0":
            lines.append(f"  Price:        {result.price}")
        if result.stop_price and result.stop_price != "0":
            lines.append(f"  Stop Price:   {result.stop_price}")
        return "\n".join(lines)
