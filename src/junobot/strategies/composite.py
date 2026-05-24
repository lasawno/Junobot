from junobot.strategies.base import Action, MarketContext, Signal, Strategy


class AndStrategy(Strategy):
    """Combines multiple strategies: emits BUY only if ALL agree on BUY,
    SELL only if ALL agree on SELL. Otherwise HOLD. Conservative."""

    name = "and"

    def __init__(self, *strategies: Strategy):
        if not strategies:
            raise ValueError("AndStrategy needs at least one inner strategy")
        self.strategies = strategies

    def evaluate(self, ctx: MarketContext) -> Signal:
        signals = [s.evaluate(ctx) for s in self.strategies]
        actions = {s.action for s in signals}
        reasons = "; ".join(f"{s.symbol}={s.action.value}({s.reason})" for s in signals)

        if actions == {Action.BUY}:
            return Signal(ctx.symbol, Action.BUY, reason=f"AND[{reasons}]")
        if actions == {Action.SELL}:
            return Signal(ctx.symbol, Action.SELL, reason=f"AND[{reasons}]")
        return Signal(ctx.symbol, Action.HOLD, reason=f"AND-disagree[{reasons}]")
