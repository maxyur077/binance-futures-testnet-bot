from pydantic import BaseModel, Field
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP = "STOP"


class OrderRequestSchema(BaseModel):
    symbol: str = Field(..., min_length=2, max_length=20, examples=["BTCUSDT"])
    side: OrderSide
    order_type: OrderType = Field(..., alias="orderType")
    quantity: float = Field(..., gt=0, examples=[0.001])
    price: float | None = Field(None, gt=0, examples=[50000.0])
    stop_price: float | None = Field(None, gt=0, alias="stopPrice", examples=[48000.0])
    time_in_force: str = Field("GTC", alias="timeInForce")

    model_config = {"populate_by_name": True}


class GridOrderRequestSchema(BaseModel):
    symbol: str = Field(..., min_length=2, max_length=20, examples=["BTCUSDT"])
    side: OrderSide
    quantity_per_order: float = Field(..., gt=0, alias="quantityPerOrder", examples=[0.001])
    lower_price: float = Field(..., gt=0, alias="lowerPrice", examples=[90000.0])
    upper_price: float = Field(..., gt=0, alias="upperPrice", examples=[100000.0])
    grid_levels: int = Field(..., ge=2, le=50, alias="gridLevels", examples=[5])
    time_in_force: str = Field("GTC", alias="timeInForce")

    model_config = {"populate_by_name": True}


class OrderResponseSchema(BaseModel):
    order_id: int = Field(..., alias="orderId")
    symbol: str
    side: str
    order_type: str = Field(..., alias="orderType")
    status: str
    orig_qty: str = Field(..., alias="origQty")
    executed_qty: str = Field(..., alias="executedQty")
    avg_price: str = Field(..., alias="avgPrice")
    price: str
    stop_price: str = Field(..., alias="stopPrice")
    time_in_force: str = Field(..., alias="timeInForce")

    model_config = {"populate_by_name": True}


class GridOrderResponseSchema(BaseModel):
    total_orders: int = Field(..., alias="totalOrders")
    successful: int
    orders: list[OrderResponseSchema]

    model_config = {"populate_by_name": True}


class ErrorResponseSchema(BaseModel):
    error: str
    detail: str
    code: int | None = None


class HealthResponseSchema(BaseModel):
    status: str
    server_time: int | None = Field(None, alias="serverTime")
    version: str

    model_config = {"populate_by_name": True}
