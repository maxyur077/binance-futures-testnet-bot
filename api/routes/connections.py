from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.database import get_db
from bot.db_models import Connection
from pydantic import BaseModel

router = APIRouter(prefix="/connections", tags=["Connections"])

class ConnectionCreate(BaseModel):
    name: str = "default"
    api_key: str
    api_secret: str

class ConnectionResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = {"from_attributes": True}

@router.post("", response_model=ConnectionResponse)
async def add_connection(conn: ConnectionCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Connection).where(Connection.name == conn.name))
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.api_key = conn.api_key
        existing.api_secret = conn.api_secret
        existing.is_active = True
        new_conn = existing
    else:
        new_conn = Connection(name=conn.name, api_key=conn.api_key, api_secret=conn.api_secret)
        db.add(new_conn)
    
    await db.commit()
    await db.refresh(new_conn)
    return new_conn

@router.get("/active", response_model=ConnectionResponse)
async def get_active_connection(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Connection).where(Connection.is_active == True))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="No active connection found")
    return conn

@router.delete("/active")
async def disconnect(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Connection).where(Connection.is_active == True))
    conn = result.scalars().first()
    if conn:
        await db.delete(conn)
        await db.commit()
    return {"status": "disconnected"}
