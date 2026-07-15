from fastapi import APIRouter, Depends

from api.dependencies import get_binance_client
from api.schemas import HealthResponseSchema
from bot import __version__
from bot.exceptions import NetworkError
from bot.client import BinanceClient

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponseSchema)
async def health_check(client: BinanceClient = Depends(get_binance_client)):
    try:
        time_data = client.server_time()
        return HealthResponseSchema(
            status="healthy",
            serverTime=time_data.get("serverTime"),
            version=__version__,
        )
    except NetworkError:
        return HealthResponseSchema(
            status="degraded",
            serverTime=None,
            version=__version__,
        )
