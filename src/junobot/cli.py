from decimal import Decimal

import typer
from rich.console import Console
from rich.table import Table

from junobot.brokers.base import OrderSide
from junobot.config import ConfigError, load_broker

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


if __name__ == "__main__":
    app()
