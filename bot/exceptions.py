class TradingBotError(Exception):
    pass


class ValidationError(TradingBotError):
    pass


class APIError(TradingBotError):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error [{code}]: {message}")


class AuthenticationError(TradingBotError):
    pass


class NetworkError(TradingBotError):
    pass
