from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None
    stop_price: float | None = None
    time_in_force: str = "GTC"


@dataclass
class OrderResult:
    order_id: int
    symbol: str
    side: str
    order_type: str
    status: str
    orig_qty: str
    executed_qty: str
    avg_price: str
    price: str
    stop_price: str
    time_in_force: str
    raw_response: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, response: dict[str, Any]) -> "OrderResult":
        return cls(
            order_id=response.get("orderId", 0),
            symbol=response.get("symbol", ""),
            side=response.get("side", ""),
            order_type=response.get("type", ""),
            status=response.get("status", ""),
            orig_qty=response.get("origQty", "0"),
            executed_qty=response.get("executedQty", "0"),
            avg_price=response.get("avgPrice", "0"),
            price=response.get("price", "0"),
            stop_price=response.get("stopPrice", "0"),
            time_in_force=response.get("timeInForce", ""),
            raw_response=response,
        )


@dataclass
class GridOrderConfig:
    symbol: str
    side: str
    quantity_per_order: float
    lower_price: float
    upper_price: float
    grid_levels: int
    time_in_force: str = "GTC"
