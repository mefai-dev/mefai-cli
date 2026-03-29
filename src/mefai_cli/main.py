"""MEFAI Engine CLI application.

All commands are registered here using Typer. Each command
calls the API client and renders output with Rich.
"""

import asyncio
import json
from typing import Optional

import typer
import websockets

from mefai_cli import __version__
from mefai_cli.api import MefaiClient
from mefai_cli.config import get_ws_url, load_config, save_config
from mefai_cli.display import (
    brand_panel,
    console,
    error_panel,
    format_percentage,
    format_pnl,
    format_price,
    print_kv_panel,
    print_stream_line,
    print_table,
    success_message,
)

app = typer.Typer(
    name="mefai",
    help="MEFAI Engine command line interface for trading and analytics.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _client() -> MefaiClient:
    """Create a new API client from current config."""
    return MefaiClient()


def _handle_error(err: Exception) -> None:
    """Display a connection or API error."""
    error_panel(f"Request failed: {err}")
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@app.command()
def configure(
    base_url: Optional[str] = typer.Option(None, help="MEFAI Engine base URL"),
    api_key: Optional[str] = typer.Option(None, help="API key for authentication"),
) -> None:
    """Set MEFAI CLI configuration values."""
    cfg = load_config()
    if base_url is not None:
        cfg["base_url"] = base_url
    if api_key is not None:
        cfg["api_key"] = api_key
    save_config(cfg)
    success_message("Configuration saved to ~/.mefai/config.yaml")


@app.command()
def version() -> None:
    """Show the CLI version."""
    brand_panel("MEFAI CLI", f"Version {__version__}", subtitle="mefai.io")


# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------

@app.command()
def status() -> None:
    """Show MEFAI Engine status."""
    try:
        data = _client().engine_status()
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel("Engine Status", data)


@app.command()
def positions() -> None:
    """List all open positions."""
    try:
        data = _client().positions()
    except Exception as e:
        _handle_error(e)
        return
    items = data.get("positions", data if isinstance(data, list) else [])
    if not items:
        brand_panel("Positions", "No open positions")
        return
    columns = [
        ("Symbol", "bold white"),
        ("Side", "cyan"),
        ("Size", "white"),
        ("Entry", "white"),
        ("PnL", "white"),
    ]
    rows = []
    for p in items:
        rows.append([
            str(p.get("symbol", "")),
            str(p.get("side", "")),
            str(p.get("size", "")),
            format_price(p.get("entry_price", 0)),
            format_pnl(p.get("pnl", 0)),
        ])
    print_table("Open Positions", columns, rows)


@app.command()
def balance() -> None:
    """Show account balance."""
    try:
        data = _client().balance()
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel("Account Balance", data)


@app.command()
def ticker(symbol: str = typer.Argument(..., help="Trading pair symbol")) -> None:
    """Get ticker price for a symbol."""
    try:
        data = _client().ticker(symbol.upper())
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel(f"Ticker: {symbol.upper()}", data)


@app.command()
def orderbook(symbol: str = typer.Argument(..., help="Trading pair symbol")) -> None:
    """Show order book for a symbol."""
    try:
        data = _client().orderbook(symbol.upper())
    except Exception as e:
        _handle_error(e)
        return
    bids = data.get("bids", [])[:10]
    asks = data.get("asks", [])[:10]
    columns = [
        ("Bid Price", "green"),
        ("Bid Size", "white"),
        ("Ask Price", "red"),
        ("Ask Size", "white"),
    ]
    rows = []
    for i in range(max(len(bids), len(asks))):
        bid = bids[i] if i < len(bids) else ["", ""]
        ask = asks[i] if i < len(asks) else ["", ""]
        rows.append([
            format_price(bid[0]) if bid[0] else "",
            str(bid[1]) if len(bid) > 1 else "",
            format_price(ask[0]) if ask[0] else "",
            str(ask[1]) if len(ask) > 1 else "",
        ])
    print_table(f"Order Book: {symbol.upper()}", columns, rows)


@app.command()
def funding(symbol: str = typer.Argument(..., help="Trading pair symbol")) -> None:
    """Show funding rate for a symbol."""
    try:
        data = _client().funding_rate(symbol.upper())
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel(f"Funding Rate: {symbol.upper()}", data)


@app.command()
def candles(
    symbol: str = typer.Argument(..., help="Trading pair symbol"),
    timeframe: str = typer.Option("1h", help="Candle timeframe (1m 5m 15m 1h 4h 1d)"),
    limit: int = typer.Option(20, help="Number of candles to fetch"),
) -> None:
    """Get candlestick data for a symbol."""
    try:
        data = _client().candles(symbol.upper(), timeframe=timeframe, limit=limit)
    except Exception as e:
        _handle_error(e)
        return
    items = data.get("candles", data if isinstance(data, list) else [])
    columns = [
        ("Time", "dim white"),
        ("Open", "white"),
        ("High", "green"),
        ("Low", "red"),
        ("Close", "bold white"),
        ("Volume", "cyan"),
    ]
    rows = []
    for c in items:
        rows.append([
            str(c.get("time", "")),
            format_price(c.get("open", 0)),
            format_price(c.get("high", 0)),
            format_price(c.get("low", 0)),
            format_price(c.get("close", 0)),
            str(c.get("volume", "")),
        ])
    print_table(f"Candles: {symbol.upper()} [{timeframe}]", columns, rows)


@app.command()
def features(symbol: str = typer.Argument(..., help="Trading pair symbol")) -> None:
    """Show computed features for a symbol."""
    try:
        data = _client().features(symbol.upper())
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel(f"Features: {symbol.upper()}", data)


# ---------------------------------------------------------------------------
# Signals and Models
# ---------------------------------------------------------------------------

@app.command()
def signals() -> None:
    """Show active trading signals."""
    try:
        data = _client().signals()
    except Exception as e:
        _handle_error(e)
        return
    items = data.get("signals", data if isinstance(data, list) else [])
    if not items:
        brand_panel("Signals", "No active signals")
        return
    columns = [
        ("Symbol", "bold white"),
        ("Direction", "cyan"),
        ("Strength", "yellow"),
        ("Source", "dim white"),
        ("Time", "dim white"),
    ]
    rows = []
    for s in items:
        rows.append([
            str(s.get("symbol", "")),
            str(s.get("direction", "")),
            str(s.get("strength", "")),
            str(s.get("source", "")),
            str(s.get("time", "")),
        ])
    print_table("Active Signals", columns, rows)


@app.command()
def models() -> None:
    """List available ML models."""
    try:
        data = _client().models()
    except Exception as e:
        _handle_error(e)
        return
    items = data.get("models", data if isinstance(data, list) else [])
    if not items:
        brand_panel("Models", "No models available")
        return
    columns = [
        ("Name", "bold white"),
        ("Type", "cyan"),
        ("Accuracy", "green"),
        ("Status", "yellow"),
    ]
    rows = []
    for m in items:
        rows.append([
            str(m.get("name", "")),
            str(m.get("type", "")),
            format_percentage(m.get("accuracy", 0)),
            str(m.get("status", "")),
        ])
    print_table("ML Models", columns, rows)


@app.command()
def predict(
    symbol: str = typer.Argument(..., help="Trading pair symbol"),
    model: Optional[str] = typer.Option(None, help="Model name to use for prediction"),
) -> None:
    """Run prediction for a symbol."""
    try:
        data = _client().predict(symbol.upper(), model=model)
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel(f"Prediction: {symbol.upper()}", data)


@app.command()
def backtest(
    symbol: str = typer.Argument(..., help="Trading pair symbol"),
    start: Optional[str] = typer.Option(None, help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, help="End date (YYYY-MM-DD)"),
) -> None:
    """Run backtest for a symbol."""
    try:
        data = _client().backtest(symbol.upper(), start=start, end=end)
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel(f"Backtest: {symbol.upper()}", data)


# ---------------------------------------------------------------------------
# Risk and Metrics
# ---------------------------------------------------------------------------

@app.command()
def metrics() -> None:
    """Show PnL and performance metrics."""
    try:
        data = _client().metrics()
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel("Performance Metrics", data)


@app.command()
def risk() -> None:
    """Show current risk status."""
    try:
        data = _client().risk()
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel("Risk Status", data)


@app.command()
def report() -> None:
    """Generate a daily trading report."""
    try:
        data = _client().report()
    except Exception as e:
        _handle_error(e)
        return
    print_kv_panel("Daily Report", data)


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

@app.command()
def stream() -> None:
    """Live WebSocket stream of market data in the terminal."""
    ws_url = get_ws_url()
    brand_panel("Live Stream", f"Connecting to {ws_url} ...", subtitle="Press Ctrl+C to stop")

    async def _stream() -> None:
        try:
            async with websockets.connect(ws_url) as ws:  # type: ignore[attr-defined]
                success_message(f"Connected to {ws_url}")
                async for message in ws:
                    try:
                        data = json.loads(message)
                        print_stream_line(data)
                    except json.JSONDecodeError:
                        console.print(f"[dim]{message}[/]")
        except Exception as e:
            error_panel(f"WebSocket error: {e}")

    try:
        asyncio.run(_stream())
    except KeyboardInterrupt:
        console.print("\n[dim]Stream stopped.[/]")


# ---------------------------------------------------------------------------
# Order Management
# ---------------------------------------------------------------------------

@app.command()
def order(
    symbol: str = typer.Argument(..., help="Trading pair symbol"),
    side: str = typer.Argument(..., help="Order side: long or short"),
    quantity: float = typer.Argument(..., help="Order quantity"),
) -> None:
    """Place a new order."""
    symbol = symbol.upper()
    side = side.lower()
    if side not in ("long", "short"):
        error_panel("Side must be 'long' or 'short'")
        raise typer.Exit(code=1)
    try:
        data = _client().place_order(symbol, side, quantity)
    except Exception as e:
        _handle_error(e)
        return
    success_message(f"Order placed: {side} {quantity} {symbol}")
    print_kv_panel("Order Result", data)


@app.command()
def close(symbol: str = typer.Argument(..., help="Trading pair symbol")) -> None:
    """Close an open position."""
    symbol = symbol.upper()
    try:
        data = _client().close_position(symbol)
    except Exception as e:
        _handle_error(e)
        return
    success_message(f"Position closed: {symbol}")
    print_kv_panel("Close Result", data)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.command()
def health() -> None:
    """Run a health check against the MEFAI Engine."""
    try:
        data = _client().health_check()
    except Exception as e:
        _handle_error(e)
        return
    ok = data.get("status") == "ok" or data.get("healthy", False)
    if ok:
        success_message("MEFAI Engine is healthy")
    else:
        error_panel("MEFAI Engine health check failed")
    print_kv_panel("Health Check", data)


if __name__ == "__main__":
    app()
