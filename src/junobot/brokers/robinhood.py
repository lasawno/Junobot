from decimal import Decimal

from junobot.brokers.base import Account, Bar, BarTimeframe, Broker, Order, OrderSide, Position, Quote


class RobinhoodBroker(Broker):
    name = "robinhood"

    def __init__(self, username: str, password: str, mfa_secret: str | None = None):
        self.username = username
        self.password = password
        self.mfa_secret = mfa_secret
        raise NotImplementedError(
            "Robinhood support is not implemented yet. Planned: robin_stocks library, "
            "TOTP-based MFA via mfa_secret. Use JUNOBOT_BROKER=alpaca for now."
        )

    def get_account(self) -> Account:
        raise NotImplementedError

    def get_positions(self) -> list[Position]:
        raise NotImplementedError

    def get_quote(self, symbol: str) -> Quote:
        raise NotImplementedError

    def get_bars(self, symbol: str, timeframe: BarTimeframe, limit: int) -> list[Bar]:
        raise NotImplementedError

    def submit_market_order(self, symbol: str, qty: Decimal, side: OrderSide) -> Order:
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError

    def is_market_open(self) -> bool:
        raise NotImplementedError
