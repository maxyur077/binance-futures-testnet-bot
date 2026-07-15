from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database import get_db
from bot.db_models import Connection
from bot.client import BinanceClient
from bot.orders import OrderService
from bot.config import API_KEY, API_SECRET

async def get_binance_client(db: AsyncSession = Depends(get_db)) -> BinanceClient:
    result = await db.execute(select(Connection).where(Connection.is_active == True))
    conn = result.scalars().first()
    
    if not conn or not conn.api_key or not conn.api_secret:
        raise HTTPException(status_code=401, detail="No active API connection found. Please add a connection.")
        
    return BinanceClient(api_key=conn.api_key, api_secret=conn.api_secret)

async def get_order_service(client: BinanceClient = Depends(get_binance_client)) -> OrderService:
    return OrderService(client)
