from decimal import Decimal

from junobot.strategies.base import Action, MarketContext, Signal, Strategy


def _mean(values: list[Decimal]) -> Decimal:
    return sum(values) / Decimal(len(values))


class SmaCrossover(Strategy):
    name = "sma_crossover"

    def __init__(self, short: int = 10, long: int = 30):
        if short >= long:
            raise ValueError(f"short ({short}) must be less than long ({long})")
        self.short = short
        self.long = long
        self._prev_diff: dict[str, Decimal] = {}

    def evaluate(self, ctx: MarketContext) -> Signal:
        closes = ctx.closes
        if len(closes) < self.long:
            return Signal(ctx.symbol, Action.HOLD, reason=f"warming up ({len(closes)}/{self.long} bars)")

        short_ma = _mean(closes[-self.short :])
        long_ma = _mean(closes[-self.long :])
        diff = short_ma - long_ma
        prev = self._prev_diff.get(ctx.symbol)
        self._prev_diff[ctx.symbol] = diff

        if prev is None:
            return Signal(ctx.symbol, Action.HOLD, reason="first observation, no crossover yet")

        if prev <= 0 and diff > 0:
            return Signal(ctx.symbol, Action.BUY, reason=f"SMA{self.short} crossed above SMA{self.long}")
        if prev >= 0 and diff < 0:
            return Signal(ctx.symbol, Action.SELL, reason=f"SMA{self.short} crossed below SMA{self.long}")
        return Signal(ctx.symbol, Action.HOLD, reason=f"diff={diff:.4f}, no crossover")
