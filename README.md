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
```

`ALPACA_PAPER=true` (default) routes everything to the paper sandbox. Flip to `false` only when you trust the code.

## Switching brokers

Set `JUNOBOT_BROKER=robinhood` in `.env` to use the Robinhood adapter (not yet implemented — currently raises `NotImplementedError`).

## Architecture

- `src/junobot/brokers/base.py` — abstract `Broker` interface + dataclasses for `Account`, `Position`, `Quote`, `Order`.
- `src/junobot/brokers/alpaca.py` — Alpaca implementation using `alpaca-py`.
- `src/junobot/brokers/robinhood.py` — stub; will use `robin_stocks` + TOTP MFA.
- `src/junobot/config.py` — loads `.env` and picks the broker via `JUNOBOT_BROKER`.
- `src/junobot/cli.py` — Typer CLI (`status`, `positions`, `quote`, `buy`, `sell`).

Strategies aren't scaffolded yet — once the broker layer is proven against paper, we'll add `src/junobot/strategies/` with a similar abstract base.
