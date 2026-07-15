import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
SERVER_TIME_ENDPOINT = "/fapi/v1/time"
EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"

API_KEY = os.getenv("BINANCE_TESTNET_API_KEY", "")
API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///trading_bot.db")

REQUEST_TIMEOUT = 30
RECV_WINDOW = 5000

SUPPORTED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT",
    "SOLUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT",
    "LINKUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT",
]

SUPPORTED_ORDER_TYPES = ["MARKET", "LIMIT", "STOP_MARKET", "STOP"]
SUPPORTED_SIDES = ["BUY", "SELL"]
TIME_IN_FORCE_OPTIONS = ["GTC", "IOC", "FOK"]
DEFAULT_TIME_IN_FORCE = "GTC"
