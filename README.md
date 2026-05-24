# Junobot

Broker-agnostic trading bot. Alpaca-first (official API, paper trading by default), with a stub for Robinhood support via `robin_stocks` to be added later.

## Setup

```bash
# Install Python 3.12 + dependencies
uv sync

# Configure credentials
cp .env.example .env
# Edit .env and paste your ALPACA_API_KEY + ALPACA_API_SECRET
```

Get Alpaca paper-trading keys at https://app.alpaca.markets/paper/dashboard/overview.

## Usage

```bash
uv run junobot status              # account summary + market open/closed
uv run junobot positions           # list open positions
uv run junobot quote AAPL          # latest bid/ask
uv run junobot buy AAPL 1          # market buy 1 share
uv run junobot sell AAPL 1         # market sell 1 share

uv run junobot-ui                  # launch Streamlit dashboard

# Run the trading engine (dry-run by default — logs signals, no orders)
uv run junobot run AAPL TSLA --short 10 --long 30 --timeframe 1Min

# Engine with real (paper) orders:
uv run junobot run AAPL --no-dry-run --size-usd 500

# News-sentiment strategy (Yahoo Finance + market RSS + VADER, fully free):
uv run junobot run AAPL --strategy news_sentiment

# Conservative composite: only trade when SMA crossover AND news agree:
uv run junobot run AAPL --strategy sma_and_news
```

`ALPACA_PAPER=true` (default) routes everything to the paper sandbox. Flip to `false` only when you trust the code.

## Switching brokers

Set `JUNOBOT_BROKER=robinhood` in `.env` to use the Robinhood adapter (not yet implemented — currently raises `NotImplementedError`).

## Architecture

- `src/junobot/brokers/base.py` — abstract `Broker` interface + dataclasses for `Account`, `Position`, `Quote`, `Order`.
- `src/junobot/brokers/alpaca.py` — Alpaca implementation using `alpaca-py`.
- `src/junobot/brokers/robinhood.py` — stub; will use `robin_stocks` + TOTP MFA.
- `src/junobot/config.py` — loads `.env` and picks the broker via `JUNOBOT_BROKER`.
- `src/junobot/cli.py` — Typer CLI (`status`, `positions`, `quote`, `buy`, `sell`, `run`).
- `src/junobot/strategies/base.py` — abstract `Strategy` + `Signal` / `Action` / `MarketContext`.
- `src/junobot/strategies/sma_crossover.py` — SMA crossover reference implementation.
- `src/junobot/engine.py` — Polling engine: ticks symbols, evaluates strategy, executes signals via the broker. Position-aware (won't double-buy, won't sell what we don't hold). Respects market hours by default.
- `src/junobot/news/feed.py` — RSS news fetcher. Yahoo Finance per-ticker headlines + general market feeds (MarketWatch, DowJones). All free, no API keys.
- `src/junobot/strategies/news_sentiment.py` — VADER sentiment on headlines, ticker-specific articles weighted 2x.
- `src/junobot/strategies/composite.py` — `AndStrategy` combines multiple strategies (conservative: trades only on agreement).

## Adding a strategy

Subclass `Strategy` and implement `evaluate(ctx: MarketContext) -> Signal`:

```python
from junobot.strategies.base import Action, MarketContext, Signal, Strategy

class MyStrategy(Strategy):
    name = "my_strategy"
    def evaluate(self, ctx: MarketContext) -> Signal:
        if ctx.latest_close < 100:
            return Signal(ctx.symbol, Action.BUY, reason="cheap")
        return Signal(ctx.symbol, Action.HOLD)
```

Register it in `strategies/__init__.py::get_strategy` and run with `--strategy my_strategy`.
