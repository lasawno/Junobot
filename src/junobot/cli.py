import logging
from decimal import Decimal

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from junobot.brokers.base import BarTimeframe, OrderSide
from junobot.config import ConfigError, load_broker
from junobot.engine import Engine, EngineConfig
from junobot.strategies import get_strategy

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


def _broker_or_exit():
    try:
        return load_broker()
    except ConfigError as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def status():
    """Show account summary and connection info."""
    broker = _broker_or_exit()
    acct = broker.get_account()
    mode = "paper" if getattr(broker, "paper", False) else "LIVE"
    console.print(f"[bold]Broker:[/bold] {broker.name} ([cyan]{mode}[/cyan])")
    table = Table(show_header=False, box=None)
    table.add_row("Cash", f"${acct.cash:,.2f}")
    table.add_row("Equity", f"${acct.equity:,.2f}")
    table.add_row("Buying power", f"${acct.buying_power:,.2f}")
    table.add_row("Currency", acct.currency)
    table.add_row("Market open", "yes" if broker.is_market_open() else "no")
    console.print(table)


@app.command()
def positions():
    """List open positions."""
    broker = _broker_or_exit()
    positions_list = broker.get_positions()
    if not positions_list:
        console.print("[dim]No open positions.[/dim]")
        return
    table = Table()
    table.add_column("Symbol")
    table.add_column("Qty", justify="right")
    table.add_column("Avg entry", justify="right")
    table.add_column("Market value", justify="right")
    table.add_column("Unrealized P/L", justify="right")
    for p in positions_list:
        pl_color = "green" if p.unrealized_pl >= 0 else "red"
        table.add_row(
            p.symbol,
            f"{p.qty}",
            f"${p.avg_entry_price:,.2f}",
            f"${p.market_value:,.2f}",
            f"[{pl_color}]${p.unrealized_pl:,.2f}[/{pl_color}]",
        )
    console.print(table)


@app.command()
def quote(symbol: str):
    """Get the latest quote for a symbol."""
    broker = _broker_or_exit()
    q = broker.get_quote(symbol.upper())
    console.print(f"[bold]{q.symbol}[/bold]  bid ${q.bid}  ask ${q.ask}")


@app.command()
def buy(symbol: str, qty: float):
    """Submit a market BUY order."""
    broker = _broker_or_exit()
    order = broker.submit_market_order(symbol.upper(), Decimal(str(qty)), OrderSide.BUY)
    console.print(f"[green]Order submitted:[/green] {order.id}  status={order.status}")


@app.command()
def sell(symbol: str, qty: float):
    """Submit a market SELL order."""
    broker = _broker_or_exit()
    order = broker.submit_market_order(symbol.upper(), Decimal(str(qty)), OrderSide.SELL)
    console.print(f"[green]Order submitted:[/green] {order.id}  status={order.status}")


@app.command()
def run(
    symbols: list[str] = typer.Argument(..., help="Tickers to watch, e.g. AAPL TSLA"),
    strategy: str = typer.Option("sma_crossover", help="Strategy name"),
    short: int = typer.Option(10, help="Short SMA window (for sma_crossover)"),
    long: int = typer.Option(30, help="Long SMA window (for sma_crossover)"),
    timeframe: str = typer.Option("1Min", help="Bar timeframe: 1Min, 5Min, 15Min, 1Hour, 1Day"),
    bar_limit: int = typer.Option(100, help="How many historical bars to request per tick"),
    poll_seconds: int = typer.Option(60, help="Seconds between ticks"),
    size_usd: float = typer.Option(1000.0, help="Dollar size per buy order"),
    dry_run: bool = typer.Option(True, help="Log signals only, don't submit orders"),
    ignore_market_hours: bool = typer.Option(False, help="Tick even when market is closed"),
):
    """Run the trading engine."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False, rich_tracebacks=True)],
    )

    broker = _broker_or_exit()
    strat = get_strategy(strategy, short=short, long=long)

    try:
        tf = BarTimeframe(timeframe)
    except ValueError:
        console.print(f"[red]Invalid timeframe:[/red] {timeframe}. Use 1Min/5Min/15Min/1Hour/1Day.")
        raise typer.Exit(code=1)

    config = EngineConfig(
        symbols=[s.upper() for s in symbols],
        timeframe=tf,
        bar_limit=bar_limit,
        poll_seconds=poll_seconds,
        position_size_usd=Decimal(str(size_usd)),
        dry_run=dry_run,
        require_market_open=not ignore_market_hours,
    )

    if not dry_run:
        mode = "paper" if getattr(broker, "paper", False) else "[red bold]LIVE[/red bold]"
        console.print(f"[yellow]⚠️  dry_run=False — orders will be submitted to {mode}.[/yellow]")

    Engine(broker, strat, config).run()


if __name__ == "__main__":
    app()
