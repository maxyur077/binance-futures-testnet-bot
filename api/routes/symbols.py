from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database import get_db
from bot.db_models import Symbol
from pydantic import BaseModel

router = APIRouter(prefix="/symbols", tags=["Symbols"])

class SymbolResponse(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    status: str

    model_config = {"from_attributes": True}

@router.get("", response_model=list[SymbolResponse])
async def search_symbols(q: str = "", db: AsyncSession = Depends(get_db)):
    query = select(Symbol).where(Symbol.status == "TRADING")
    if q:
        query = query.where(Symbol.symbol.like(f"%{q}%"))
    query = query.limit(20)
    result = await db.execute(query)
    symbols = result.scalars().all()
    return symbols
