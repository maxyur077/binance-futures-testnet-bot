import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_order_service
from bot.orders import OrderService
from api.schemas import (
    OrderRequestSchema,
    OrderResponseSchema,
    GridOrderRequestSchema,
    GridOrderResponseSchema,
    ErrorResponseSchema,
)
from bot.exceptions import TradingBotError, ValidationError, APIError, NetworkError

logger = logging.getLogger("bot.api.orders")

router = APIRouter(prefix="/orders", tags=["Orders"])


def _error_response(exc: TradingBotError) -> JSONResponse:
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponseSchema(
                error="validation_error", detail=str(exc)
            ).model_dump(),
        )
    if isinstance(exc, APIError):
        return JSONResponse(
            status_code=502,
            content=ErrorResponseSchema(
                error="api_error", detail=exc.message, code=exc.code
            ).model_dump(),
        )
    if isinstance(exc, NetworkError):
        return JSONResponse(
            status_code=503,
            content=ErrorResponseSchema(
                error="network_error", detail=str(exc)
            ).model_dump(),
        )
    return JSONResponse(
        status_code=500,
        content=ErrorResponseSchema(
            error="internal_error", detail=str(exc)
        ).model_dump(),
    )


@router.post("", response_model=OrderResponseSchema)
async def place_order(request: OrderRequestSchema, service: OrderService = Depends(get_order_service)):
    try:
        result = service.place_order(
            symbol=request.symbol,
            side=request.side.value,
            order_type=request.order_type.value,
            quantity=request.quantity,
            price=request.price,
            stop_price=request.stop_price,
            time_in_force=request.time_in_force,
        )
        return OrderResponseSchema(
            orderId=result.order_id,
            symbol=result.symbol,
            side=result.side,
            orderType=result.order_type,
            status=result.status,
            origQty=result.orig_qty,
            executedQty=result.executed_qty,
            avgPrice=result.avg_price,
            price=result.price,
            stopPrice=result.stop_price,
            timeInForce=result.time_in_force,
        )
    except TradingBotError as exc:
        logger.error("Order failed: %s", exc)
        return _error_response(exc)


@router.post("/grid", response_model=GridOrderResponseSchema)
async def place_grid_order(request: GridOrderRequestSchema, service: OrderService = Depends(get_order_service)):
    try:
        results = service.place_grid_orders(
            symbol=request.symbol,
            side=request.side.value,
            quantity_per_order=request.quantity_per_order,
            lower_price=request.lower_price,
            upper_price=request.upper_price,
            grid_levels=request.grid_levels,
            time_in_force=request.time_in_force,
        )
        order_responses = [
            OrderResponseSchema(
                orderId=r.order_id,
                symbol=r.symbol,
                side=r.side,
                orderType=r.order_type,
                status=r.status,
                origQty=r.orig_qty,
                executedQty=r.executed_qty,
                avgPrice=r.avg_price,
                price=r.price,
                stopPrice=r.stop_price,
                timeInForce=r.time_in_force,
            )
            for r in results
        ]
        return GridOrderResponseSchema(
            totalOrders=len(results),
            successful=len(results),
            orders=order_responses,
        )
    except TradingBotError as exc:
        logger.error("Grid order failed: %s", exc)
        return _error_response(exc)
