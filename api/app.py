from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes.health import router as health_router
from api.routes.orders import router as orders_router
from api.routes.symbols import router as symbols_router
from api.routes.connections import router as connections_router
from bot.logging_config import setup_logging
from bot.database import engine, Base, AsyncSessionLocal
from bot.db_models import Symbol
import httpx
from bot.config import BASE_URL, EXCHANGE_INFO_ENDPOINT
from bot.logging_config import setup_logging

setup_logging()

BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Fetch symbols from Binance Testnet
    try:
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            resp = await client.get(EXCHANGE_INFO_ENDPOINT)
            if resp.status_code == 200:
                data = resp.json()
                symbols_data = data.get("symbols", [])
                
                async with AsyncSessionLocal() as session:
                    for s_data in symbols_data:
                        if s_data.get("contractType") == "PERPETUAL":
                            s = await session.get(Symbol, s_data["symbol"])
                            if not s:
                                s = Symbol(symbol=s_data["symbol"])
                                session.add(s)
                            s.base_asset = s_data.get("baseAsset", "")
                            s.quote_asset = s_data.get("quoteAsset", "")
                            s.status = s_data.get("status", "")
                    await session.commit()
    except Exception as e:
        print(f"Failed to fetch symbols on startup: {e}")
        
    yield

app = FastAPI(
    title="Binance Futures Testnet Trading Bot",
    description="Place MARKET, LIMIT, STOP_MARKET, STOP, and Grid orders on Binance Futures Testnet",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(UI_DIR / "templates"))

app.include_router(health_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(symbols_router, prefix="/api")
app.include_router(connections_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def serve_ui(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})
