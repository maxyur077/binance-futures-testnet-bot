import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from bot.config import API_KEY, API_SECRET, BASE_URL, REQUEST_TIMEOUT, RECV_WINDOW
from bot.exceptions import APIError, AuthenticationError, NetworkError

logger = logging.getLogger("bot.client")


class BinanceClient:
    def __init__(
        self,
        api_key: str = API_KEY,
        api_secret: str = API_SECRET,
        base_url: str = BASE_URL,
    ):
        if not api_key or not api_secret:
            raise AuthenticationError(
                "API credentials not configured. "
                "Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in .env"
            )
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=REQUEST_TIMEOUT,
            headers={"X-MBX-APIKEY": self._api_key},
        )
        self._time_offset = 0
        self._time_synced = False

    def sync_time(self) -> None:
        try:
            local_time_before = int(time.time() * 1000)
            response = self._client.get("/fapi/v1/time")
            response.raise_for_status()
            server_time = response.json()["serverTime"]
            local_time_after = int(time.time() * 1000)
            local_time = (local_time_before + local_time_after) // 2
            self._time_offset = server_time - local_time
            self._time_synced = True
            logger.info("Time synced with Binance. Offset: %d ms", self._time_offset)
        except Exception as exc:
            logger.warning("Failed to sync time: %s", exc)

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _signed_request(
        self, method: str, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not self._time_synced:
            self.sync_time()

        params = params or {}
        params["timestamp"] = int(time.time() * 1000) + self._time_offset
        params["recvWindow"] = RECV_WINDOW

        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params["signature"] = signature

        log_params = {k: v for k, v in params.items() if k != "signature"}
        logger.info("API Request: %s %s | params=%s", method, endpoint, log_params)

        try:
            response = self._client.request(method, endpoint, params=params)
        except httpx.ConnectError as exc:
            logger.error("Connection failed: %s", exc)
            raise NetworkError(f"Failed to connect to {self._base_url}: {exc}") from exc
        except httpx.TimeoutException as exc:
            logger.error("Request timed out: %s", exc)
            raise NetworkError(f"Request timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            logger.error("HTTP error: %s", exc)
            raise NetworkError(f"HTTP error: {exc}") from exc

        try:
            data = response.json()
        except Exception:
            logger.error("Failed to parse response: %s", response.text)
            raise APIError(-1, f"Invalid JSON response: {response.text}")

        logger.info("API Response: status=%d | body=%s", response.status_code, data)

        if response.status_code >= 400:
            error_code = data.get("code", response.status_code)
            error_msg = data.get("msg", response.text)
            logger.error("API Error [%s]: %s", error_code, error_msg)
            raise APIError(error_code, error_msg)

        return data

    def server_time(self) -> dict[str, Any]:
        try:
            response = self._client.get("/fapi/v1/time")
            return response.json()
        except httpx.HTTPError as exc:
            raise NetworkError(f"Failed to fetch server time: {exc}") from exc

    def place_order(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._signed_request("POST", "/fapi/v1/order", params)

    def get_order(self, symbol: str, order_id: int) -> dict[str, Any]:
        return self._signed_request(
            "GET", "/fapi/v1/order", {"symbol": symbol, "orderId": order_id}
        )

    def get_exchange_info(self) -> dict[str, Any]:
        try:
            response = self._client.get("/fapi/v1/exchangeInfo")
            return response.json()
        except httpx.HTTPError as exc:
            raise NetworkError(f"Failed to fetch exchange info: {exc}") from exc

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
