from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class BarTimeframe(str, Enum):
    MINUTE = "1Min"
    FIVE_MINUTE = "5Min"
    FIFTEEN_MINUTE = "15Min"
    HOUR = "1Hour"
    DAY = "1Day"


@dataclass(frozen=True)
class Account:
    cash: Decimal
    equity: Decimal
    buying_power: Decimal
    currency: str


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: Decimal
    avg_entry_price: Decimal
    market_value: Decimal
    unrealized_pl: Decimal


@dataclass(frozen=True)
class Quote:
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal | None


@dataclass(frozen=True)
class Bar:
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class Order:
    id: str
    symbol: str
    qty: Decimal
    side: OrderSide
    status: str
    filled_qty: Decimal
    filled_avg_price: Decimal | None


class Broker(ABC):
    name: str

    @abstractmethod
    def get_account(self) -> Account: ...

    @abstractmethod
    def get_positions(self) -> list[Position]: ...

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote: ...

    @abstractmethod
    def get_bars(self, symbol: str, timeframe: BarTimeframe, limit: int) -> list[Bar]: ...

    @abstractmethod
    def submit_market_order(self, symbol: str, qty: Decimal, side: OrderSide) -> Order: ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> None: ...

    @abstractmethod
    def is_market_open(self) -> bool: ...
