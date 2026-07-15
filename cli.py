import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, FloatPrompt, IntPrompt
from rich.text import Text
from rich import box

from bot.client import BinanceClient
from bot.orders import OrderService
from bot.models import OrderRequest
from bot.logging_config import setup_logging
from bot.exceptions import TradingBotError, ValidationError, APIError, NetworkError, AuthenticationError
from bot.config import SUPPORTED_SYMBOLS, SUPPORTED_ORDER_TYPES, SUPPORTED_SIDES

console = Console()

BANNER = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗
║          BINANCE FUTURES TESTNET TRADING BOT                ║
║                    v1.0.0                                   ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]
"""


def display_order_request(request: OrderRequest) -> None:
    table = Table(
        title="Order Request",
        box=box.ROUNDED,
        title_style="bold yellow",
        border_style="yellow",
    )
    table.add_column("Parameter", style="cyan", width=15)
    table.add_column("Value", style="white", width=25)

    table.add_row("Symbol", request.symbol)
    table.add_row("Side", f"[green]{request.side}[/green]" if request.side == "BUY" else f"[red]{request.side}[/red]")
    table.add_row("Type", request.order_type)
    table.add_row("Quantity", str(request.quantity))
    if request.price is not None:
        table.add_row("Price", str(request.price))
    if request.stop_price is not None:
        table.add_row("Stop Price", str(request.stop_price))
    table.add_row("Time in Force", request.time_in_force)

    console.print(table)


def display_order_result(service: OrderService, result) -> None:
    status_color = "green" if result.status in ("NEW", "FILLED", "PARTIALLY_FILLED") else "red"
    table = Table(
        title="Order Response",
        box=box.ROUNDED,
        title_style=f"bold {status_color}",
        border_style=status_color,
    )
    table.add_column("Field", style="cyan", width=15)
    table.add_column("Value", style="white", width=30)

    table.add_row("Order ID", str(result.order_id))
    table.add_row("Symbol", result.symbol)
    table.add_row("Side", f"[green]{result.side}[/green]" if result.side == "BUY" else f"[red]{result.side}[/red]")
    table.add_row("Type", result.order_type)
    table.add_row("Status", f"[{status_color}]{result.status}[/{status_color}]")
    table.add_row("Orig Qty", result.orig_qty)
    table.add_row("Executed Qty", result.executed_qty)
    table.add_row("Avg Price", result.avg_price)
    if result.price and result.price != "0":
        table.add_row("Price", result.price)
    if result.stop_price and result.stop_price != "0":
        table.add_row("Stop Price", result.stop_price)

    console.print(table)
    console.print(f"\n  [bold {status_color}]✓ Order placed successfully[/bold {status_color}]\n")


def display_error(message: str) -> None:
    console.print(Panel(
        f"[bold red]✗ {message}[/bold red]",
        border_style="red",
        title="Error",
    ))


@click.group()
def cli():
    setup_logging()


@cli.command()
@click.option("--symbol", "-s", type=str, help="Trading pair (e.g., BTCUSDT)")
@click.option("--side", "-S", type=click.Choice(SUPPORTED_SIDES, case_sensitive=False), help="Order side")
@click.option("--type", "-t", "order_type", type=click.Choice(SUPPORTED_ORDER_TYPES, case_sensitive=False), help="Order type")
@click.option("--quantity", "-q", type=float, help="Order quantity")
@click.option("--price", "-p", type=float, default=None, help="Limit price (required for LIMIT/STOP)")
@click.option("--stop-price", "-sp", type=float, default=None, help="Stop price (required for STOP_MARKET/STOP)")
def order(symbol, side, order_type, quantity, price, stop_price):
    console.print(BANNER)

    try:
        request = OrderRequest(
            symbol=symbol.upper(),
            side=side.upper(),
            order_type=order_type.upper(),
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        display_order_request(request)
        console.print()

        with BinanceClient() as client:
            service = OrderService(client)
            result = service.place_order(
                symbol=request.symbol,
                side=request.side,
                order_type=request.order_type,
                quantity=request.quantity,
                price=request.price,
                stop_price=request.stop_price,
            )
            display_order_result(service, result)

    except ValidationError as exc:
        display_error(str(exc))
        sys.exit(1)
    except AuthenticationError as exc:
        display_error(str(exc))
        sys.exit(1)
    except APIError as exc:
        display_error(f"Binance API [{exc.code}]: {exc.message}")
        sys.exit(1)
    except NetworkError as exc:
        display_error(str(exc))
        sys.exit(1)
    except TradingBotError as exc:
        display_error(str(exc))
        sys.exit(1)


@cli.command()
@click.option("--symbol", "-s", type=str, help="Trading pair")
@click.option("--side", "-S", type=click.Choice(SUPPORTED_SIDES, case_sensitive=False), help="Order side")
@click.option("--quantity", "-q", type=float, help="Quantity per grid level")
@click.option("--lower", "-l", type=float, help="Lower price bound")
@click.option("--upper", "-u", type=float, help="Upper price bound")
@click.option("--levels", "-n", type=int, help="Number of grid levels")
def grid(symbol, side, quantity, lower, upper, levels):
    console.print(BANNER)

    try:
        console.print(Panel(
            f"[cyan]Grid Order: {symbol.upper()} | {side.upper()} | "
            f"{levels} levels from {lower} to {upper} | qty={quantity} each[/cyan]",
            title="Grid Configuration",
            border_style="cyan",
        ))

        with BinanceClient() as client:
            service = OrderService(client)
            results = service.place_grid_orders(
                symbol=symbol.upper(),
                side=side.upper(),
                quantity_per_order=quantity,
                lower_price=lower,
                upper_price=upper,
                grid_levels=levels,
            )

            table = Table(
                title=f"Grid Results — {len(results)} Orders Placed",
                box=box.ROUNDED,
                title_style="bold green",
                border_style="green",
            )
            table.add_column("#", style="dim", width=4)
            table.add_column("Order ID", style="cyan", width=12)
            table.add_column("Price", style="yellow", width=12)
            table.add_column("Qty", width=10)
            table.add_column("Status", width=12)

            for i, r in enumerate(results, 1):
                status_color = "green" if r.status in ("NEW", "FILLED") else "red"
                table.add_row(
                    str(i),
                    str(r.order_id),
                    r.price,
                    r.orig_qty,
                    f"[{status_color}]{r.status}[/{status_color}]",
                )

            console.print(table)
            console.print(f"\n  [bold green]✓ Grid strategy executed: {len(results)}/{levels} orders placed[/bold green]\n")

    except TradingBotError as exc:
        display_error(str(exc))
        sys.exit(1)


@cli.command()
def interactive():
    console.print(BANNER)

    while True:
        console.print("\n[bold cyan]Select Action:[/bold cyan]")
        console.print("  [1] Place Order")
        console.print("  [2] Place Grid Orders")
        console.print("  [3] Health Check")
        console.print("  [0] Exit")

        choice = Prompt.ask("\n[bold]Choose", choices=["0", "1", "2", "3"], default="1")

        if choice == "0":
            console.print("[dim]Goodbye.[/dim]")
            break

        if choice == "3":
            try:
                with BinanceClient() as client:
                    time_data = client.server_time()
                    console.print(Panel(
                        f"[green]✓ Connected | Server Time: {time_data.get('serverTime')}[/green]",
                        title="Health",
                        border_style="green",
                    ))
            except TradingBotError as exc:
                display_error(str(exc))
            continue

        try:
            console.print(f"\n[bold]Available symbols:[/bold] {', '.join(SUPPORTED_SYMBOLS[:10])}...")
            symbol = Prompt.ask("[cyan]Symbol[/cyan]", default="BTCUSDT").upper()

            side = Prompt.ask("[cyan]Side[/cyan]", choices=["BUY", "SELL"], default="BUY")

            if choice == "1":
                order_type = Prompt.ask(
                    "[cyan]Order Type[/cyan]",
                    choices=SUPPORTED_ORDER_TYPES,
                    default="MARKET",
                )

                quantity = FloatPrompt.ask("[cyan]Quantity[/cyan]", default=0.001)

                price = None
                stop_price = None

                if order_type in ("LIMIT", "STOP"):
                    price = FloatPrompt.ask("[cyan]Price[/cyan]")

                if order_type in ("STOP_MARKET", "STOP"):
                    stop_price = FloatPrompt.ask("[cyan]Stop Price[/cyan]")

                request = OrderRequest(
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=price,
                    stop_price=stop_price,
                )
                display_order_request(request)

                if not Confirm.ask("\n[yellow]Confirm order?[/yellow]", default=True):
                    console.print("[dim]Order cancelled.[/dim]")
                    continue

                with BinanceClient() as client:
                    service = OrderService(client)
                    result = service.place_order(
                        symbol=request.symbol,
                        side=request.side,
                        order_type=request.order_type,
                        quantity=request.quantity,
                        price=request.price,
                        stop_price=request.stop_price,
                    )
                    display_order_result(service, result)

            elif choice == "2":
                quantity = FloatPrompt.ask("[cyan]Quantity per level[/cyan]", default=0.001)
                lower = FloatPrompt.ask("[cyan]Lower price[/cyan]")
                upper = FloatPrompt.ask("[cyan]Upper price[/cyan]")
                levels = IntPrompt.ask("[cyan]Grid levels[/cyan]", default=5)

                console.print(Panel(
                    f"[cyan]Grid: {symbol} {side} | {levels} levels | "
                    f"{lower:.2f} → {upper:.2f} | qty={quantity}[/cyan]",
                    title="Grid Preview",
                    border_style="cyan",
                ))

                if not Confirm.ask("\n[yellow]Confirm grid?[/yellow]", default=True):
                    console.print("[dim]Grid cancelled.[/dim]")
                    continue

                with BinanceClient() as client:
                    service = OrderService(client)
                    results = service.place_grid_orders(
                        symbol=symbol,
                        side=side,
                        quantity_per_order=quantity,
                        lower_price=lower,
                        upper_price=upper,
                        grid_levels=levels,
                    )
                    console.print(f"[bold green]✓ {len(results)} grid orders placed[/bold green]")

        except TradingBotError as exc:
            display_error(str(exc))
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/dim]")
            break


if __name__ == "__main__":
    cli()
