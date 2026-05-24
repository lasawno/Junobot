import logging
import time
from dataclasses import dataclass, field
from decimal import Decimal

from junobot.brokers import Bar, BarTimeframe, Broker, OrderSide
from junobot.strategies import Action, MarketContext, Signal, Strategy

log = logging.getLogger("junobot.engine")


@dataclass
class EngineConfig:
    symbols: list[str]
    timeframe: BarTimeframe = BarTimeframe.MINUTE
    bar_limit: int = 100
    poll_seconds: int = 60
    position_size_usd: Decimal = Decimal("1000")
    dry_run: bool = True  # Log signals but don't submit orders
    require_market_open: bool = True


@dataclass
class EngineState:
    ticks: int = 0
    signals_emitted: int = 0
    orders_submitted: int = 0
    last_signal: dict[str, Signal] = field(default_factory=dict)


class Engine:
    def __init__(self, broker: Broker, strategy: Strategy, config: EngineConfig):
        self.broker = broker
        self.strategy = strategy
        self.config = config
        self.state = EngineState()
        self._running = False

    def _fetch_bars(self, symbol: str) -> list[Bar]:
        return self.broker.get_bars(symbol, self.config.timeframe, self.config.bar_limit)

    def _held_qty(self, symbol: str) -> Decimal:
        for p in self.broker.get_positions():
            if p.symbol == symbol:
                return p.qty
        return Decimal(0)

    def _execute(self, signal: Signal) -> None:
        if signal.action == Action.HOLD:
            return

        if self.config.dry_run:
            log.info("[dry-run] would %s %s (%s)", signal.action.value, signal.symbol, signal.reason)
            return

        held = self._held_qty(signal.symbol)

        if signal.action == Action.BUY:
            if held > 0:
                log.info("skip BUY %s: already long %s shares", signal.symbol, held)
                return
            quote = self.broker.get_quote(signal.symbol)
            if quote.ask <= 0:
                log.warning("skip BUY %s: invalid ask price %s", signal.symbol, quote.ask)
                return
            qty = (self.config.position_size_usd / quote.ask).quantize(Decimal("1"))
            if qty <= 0:
                log.warning("skip BUY %s: computed qty %s (price=%s, size=%s)",
                            signal.symbol, qty, quote.ask, self.config.position_size_usd)
                return
            order = self.broker.submit_market_order(signal.symbol, qty, OrderSide.BUY)
            self.state.orders_submitted += 1
            log.info("BUY %s x%s submitted: id=%s status=%s", signal.symbol, qty, order.id, order.status)

        elif signal.action == Action.SELL:
            if held <= 0:
                log.info("skip SELL %s: no position to sell", signal.symbol)
                return
            order = self.broker.submit_market_order(signal.symbol, held, OrderSide.SELL)
            self.state.orders_submitted += 1
            log.info("SELL %s x%s submitted: id=%s status=%s", signal.symbol, held, order.id, order.status)

    def tick(self) -> list[Signal]:
        if self.config.require_market_open and not self.broker.is_market_open():
            log.debug("market closed, skipping tick")
            return []

        signals = []
        for symbol in self.config.symbols:
            try:
                bars = self._fetch_bars(symbol)
                ctx = MarketContext(symbol=symbol, bars=bars)
                signal = self.strategy.evaluate(ctx)
                signals.append(signal)
                self.state.last_signal[symbol] = signal
                self.state.signals_emitted += 1
                log.info("%s: %s (%s) [bars=%d]", symbol, signal.action.value, signal.reason, len(bars))
                self._execute(signal)
            except Exception as e:
                log.exception("error processing %s: %s", symbol, e)
        self.state.ticks += 1
        return signals

    def run(self) -> None:
        self._running = True
        log.info(
            "engine starting: broker=%s strategy=%s symbols=%s dry_run=%s poll=%ds",
            self.broker.name, self.strategy.name, self.config.symbols,
            self.config.dry_run, self.config.poll_seconds,
        )
        try:
            while self._running:
                self.tick()
                time.sleep(self.config.poll_seconds)
        except KeyboardInterrupt:
            log.info("engine stopped (ctrl+c)")
        finally:
            self._running = False

    def stop(self) -> None:
        self._running = False
