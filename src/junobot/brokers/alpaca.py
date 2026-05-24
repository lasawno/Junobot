from decimal import Decimal

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide as AlpacaOrderSide
from alpaca.trading.enums import TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from junobot.brokers.base import Account, Broker, Order, OrderSide, Position, Quote


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
