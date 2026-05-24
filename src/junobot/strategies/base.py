from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from junobot.brokers.base import Bar


class Action(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(frozen=True)
class MarketContext:
    symbol: str
    bars: list[Bar]  # oldest -> newest

    @property
    def closes(self) -> list[Decimal]:
        return [b.close for b in self.bars]

    @property
    def latest_close(self) -> Decimal:
        return self.bars[-1].close


@dataclass(frozen=True)
class Signal:
    symbol: str
    action: Action
    reason: str = ""


class Strategy(ABC):
    name: str

    @abstractmethod
    def evaluate(self, ctx: MarketContext) -> Signal: ...
