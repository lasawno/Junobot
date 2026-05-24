from datetime import datetime, timedelta, timezone
from decimal import Decimal

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide as AlpacaOrderSide
from alpaca.trading.enums import TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from junobot.brokers.base import Account, Bar, BarTimeframe, Broker, Order, OrderSide, Position, Quote

_TIMEFRAME_MAP = {
    BarTimeframe.MINUTE: TimeFrame(1, TimeFrameUnit.Minute),
    BarTimeframe.FIVE_MINUTE: TimeFrame(5, TimeFrameUnit.Minute),
    BarTimeframe.FIFTEEN_MINUTE: TimeFrame(15, TimeFrameUnit.Minute),
    BarTimeframe.HOUR: TimeFrame(1, TimeFrameUnit.Hour),
    BarTimeframe.DAY: TimeFrame(1, TimeFrameUnit.Day),
}

# Minutes of clock time per bar, padded for off-hours and weekends/holidays.
# Used to compute a generous `start` so `limit` actually returns N bars.
_LOOKBACK_PAD_MINUTES = {
    BarTimeframe.MINUTE: 3,
    BarTimeframe.FIVE_MINUTE: 15,
    BarTimeframe.FIFTEEN_MINUTE: 45,
    BarTimeframe.HOUR: 180,
    BarTimeframe.DAY: 60 * 24 * 3,  # 3 calendar days per trading day (weekend/holiday slack)
}


class AlpacaBroker(Broker):
    name = "alpaca"

    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        self._trading = TradingClient(api_key, api_secret, paper=paper)
        self._data = StockHistoricalDataClient(api_key, api_secret)
        self.paper = paper

    def get_account(self) -> Account:
        a = self._trading.get_account()
        return Account(
            cash=Decimal(a.cash),
            equity=Decimal(a.equity),
            buying_power=Decimal(a.buying_power),
            currency=a.currency,
        )

    def get_positions(self) -> list[Position]:
        return [
            Position(
                symbol=p.symbol,
                qty=Decimal(p.qty),
                avg_entry_price=Decimal(p.avg_entry_price),
                market_value=Decimal(p.market_value),
                unrealized_pl=Decimal(p.unrealized_pl),
            )
            for p in self._trading.get_all_positions()
        ]

    def get_quote(self, symbol: str) -> Quote:
        req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        result = self._data.get_stock_latest_quote(req)
        q = result[symbol]
        return Quote(
            symbol=symbol,
            bid=Decimal(str(q.bid_price)),
            ask=Decimal(str(q.ask_price)),
            last=None,
        )

    def get_bars(self, symbol: str, timeframe: BarTimeframe, limit: int) -> list[Bar]:
        lookback_minutes = limit * _LOOKBACK_PAD_MINUTES[timeframe]
        start = datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes)
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=_TIMEFRAME_MAP[timeframe],
            start=start,
            limit=limit,
        )
        result = self._data.get_stock_bars(req)
        bars_data = result.data.get(symbol, [])
        return [
            Bar(
                symbol=symbol,
                timestamp=b.timestamp,
                open=Decimal(str(b.open)),
                high=Decimal(str(b.high)),
                low=Decimal(str(b.low)),
                close=Decimal(str(b.close)),
                volume=Decimal(str(b.volume)),
            )
            for b in bars_data
        ]

    def submit_market_order(self, symbol: str, qty: Decimal, side: OrderSide) -> Order:
        alpaca_side = AlpacaOrderSide.BUY if side == OrderSide.BUY else AlpacaOrderSide.SELL
        req = MarketOrderRequest(
            symbol=symbol,
            qty=float(qty),
            side=alpaca_side,
            time_in_force=TimeInForce.DAY,
        )
        o = self._trading.submit_order(req)
        return Order(
            id=str(o.id),
            symbol=o.symbol,
            qty=Decimal(str(o.qty)),
            side=side,
            status=str(o.status),
            filled_qty=Decimal(str(o.filled_qty or 0)),
            filled_avg_price=Decimal(str(o.filled_avg_price)) if o.filled_avg_price else None,
        )

    def cancel_order(self, order_id: str) -> None:
        self._trading.cancel_order_by_id(order_id)

    def is_market_open(self) -> bool:
        return self._trading.get_clock().is_open
