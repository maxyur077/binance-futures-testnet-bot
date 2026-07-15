# Binance Futures Testnet Trading Bot

A production-grade Python trading bot for placing orders on Binance Futures USDT-M Testnet. Features a FastAPI REST API backend, a modern web UI built with Tailwind CSS, and a Rich-powered interactive CLI.

## Features

- **Order Types**: MARKET, LIMIT, STOP_MARKET, STOP (Stop-Limit)
- **Grid Strategy**: Place multiple LIMIT orders at evenly spaced price intervals
- **Web UI**: Dark glassmorphism interface with real-time validation and order history
- **CLI**: Both direct command mode and interactive menu mode with Rich formatting
- **REST API**: Full FastAPI backend with auto-generated OpenAPI documentation
- **Logging**: JSON-structured rotating file logs + coloured console output

## Prerequisites

- Python 3.10+
- Binance Futures Testnet account ([register here](https://testnet.binancefuture.com))
- Testnet API Key and Secret

## Setup

```bash
git clone <repository-url>
cd binance_testnet

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Configure API Credentials

```bash
cp .env.example .env
```

Edit `.env` and add your testnet credentials:

```
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

## Usage

### Web UI + API Server

```bash
python main.py
```

Open http://localhost:8000 for the trading UI.
API docs available at http://localhost:8000/docs.

### CLI — Direct Commands

**Market Order:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Limit Order:**
```bash
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 4000
```

**Stop-Market Order:**
```bash
python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 90000
```

**Stop-Limit Order:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 95000 --stop-price 94000
```

**Grid Strategy:**
```bash
python cli.py grid --symbol BTCUSDT --side BUY --quantity 0.001 --lower 90000 --upper 100000 --levels 5
```

### CLI — Interactive Mode

```bash
python cli.py interactive
```

Provides a menu-driven interface with prompts, validation, and order confirmation.

### REST API Examples

**Place a Market Order:**
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "side": "BUY", "orderType": "MARKET", "quantity": 0.001}'
```

**Place a Grid:**
```bash
curl -X POST http://localhost:8000/api/orders/grid \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "side": "BUY", "quantityPerOrder": 0.001, "lowerPrice": 90000, "upperPrice": 100000, "gridLevels": 5}'
```

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

## Project Structure

```
binance_testnet/
├── bot/
│   ├── __init__.py          # Package version
│   ├── config.py            # Environment and constants
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── logging_config.py    # Structured logging setup
│   ├── models.py            # Order dataclasses
│   ├── validators.py        # Input validation
│   ├── client.py            # Binance HTTP client with HMAC signing
│   └── orders.py            # Order placement and grid logic
├── api/
│   ├── __init__.py
│   ├── app.py               # FastAPI application
│   ├── schemas.py           # Pydantic request/response models
│   ├── dependencies.py      # Dependency injection
│   └── routes/
│       ├── __init__.py
│       ├── health.py        # Health check endpoint
│       └── orders.py        # Order endpoints
├── ui/
│   ├── templates/
│   │   └── index.html       # Main trading interface
│   └── static/
│       ├── css/
│       │   └── style.css    # Custom styles
│       └── js/
│           └── app.js       # Frontend logic
├── logs/                    # Generated log files
├── cli.py                   # CLI entry point
├── main.py                  # FastAPI server entry point
├── .env.example             # Credentials template
├── .gitignore
├── requirements.txt
└── README.md
```

## Assumptions

1. Binance Futures Testnet at `https://testnet.binancefuture.com` is used for all API calls
2. Account operates in One-Way mode (default `positionSide=BOTH`)
3. `timeInForce=GTC` (Good Till Cancel) is the default for LIMIT orders
4. No leverage or margin configuration is managed — testnet defaults apply
5. The STOP_MARKET and STOP order types use `/fapi/v1/order` with `stopPrice`
6. Grid strategy places individual LIMIT orders sequentially

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log` in JSON format with automatic rotation (5MB max, 3 backups). Console output uses coloured formatting for readability.

## API Documentation

When the server is running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
