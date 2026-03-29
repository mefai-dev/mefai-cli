"""Rich formatting helpers for MEFAI CLI.

Provides reusable functions for rendering tables and panels
and status indicators with consistent styling.
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()

BRAND_COLOR = "cyan"
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
MUTED_COLOR = "dim white"


def brand_panel(title: str, content: str, subtitle: str | None = None) -> None:
    """Display a branded panel with MEFAI styling."""
    panel = Panel(
        content,
        title=f"[bold {BRAND_COLOR}]{title}[/]",
        subtitle=f"[{MUTED_COLOR}]{subtitle}[/]" if subtitle else None,
        border_style=BRAND_COLOR,
        padding=(1, 2),
    )
    console.print(panel)


def error_panel(message: str) -> None:
    """Display an error panel."""
    panel = Panel(
        f"[{ERROR_COLOR}]{message}[/]",
        title=f"[bold {ERROR_COLOR}]Error[/]",
        border_style=ERROR_COLOR,
        padding=(1, 2),
    )
    console.print(panel)


def success_message(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold {SUCCESS_COLOR}][ok][/] {message}")


def warning_message(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold {WARNING_COLOR}][warn][/] {message}")


def make_table(title: str, columns: list[tuple[str, str]], rows: list[list[str]]) -> Table:
    """Build a Rich table with branded styling.

    Each column is a tuple of (header_name and style).
    """
    table = Table(
        title=f"[bold {BRAND_COLOR}]{title}[/]",
        border_style=BRAND_COLOR,
        header_style=f"bold {BRAND_COLOR}",
        show_lines=True,
    )
    for col_name, col_style in columns:
        table.add_column(col_name, style=col_style)
    for row in rows:
        table.add_row(*row)
    return table


def print_table(title: str, columns: list[tuple[str, str]], rows: list[list[str]]) -> None:
    """Build and print a Rich table."""
    console.print(make_table(title, columns, rows))


def print_kv_panel(title: str, data: dict[str, Any]) -> None:
    """Print a key value panel from a dictionary."""
    lines: list[str] = []
    for key, value in data.items():
        label = key.replace("_", " ").title()
        lines.append(f"[bold white]{label}:[/] {value}")
    brand_panel(title, "\n".join(lines))


def format_price(value: float | str) -> str:
    """Format a price value with color."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    return f"[bold white]{num:,.4f}[/]"


def format_pnl(value: float | str) -> str:
    """Format a PnL value with green/red color."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    color = SUCCESS_COLOR if num >= 0 else ERROR_COLOR
    sign = "+" if num >= 0 else ""
    return f"[bold {color}]{sign}{num:,.2f}[/]"


def format_percentage(value: float | str) -> str:
    """Format a percentage value with color."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    color = SUCCESS_COLOR if num >= 0 else ERROR_COLOR
    sign = "+" if num >= 0 else ""
    return f"[{color}]{sign}{num:.2f}%[/]"


def status_dot(is_ok: bool) -> Text:
    """Return a colored status dot."""
    if is_ok:
        return Text("  online", style=f"bold {SUCCESS_COLOR}")
    return Text("  offline", style=f"bold {ERROR_COLOR}")


def print_stream_line(data: dict[str, Any]) -> None:
    """Print a single streaming data line."""
    symbol = data.get("symbol", "???")
    price = data.get("price", 0)
    change = data.get("change_pct", 0)
    formatted = f"[bold white]{symbol}[/]  {format_price(price)}  {format_percentage(change)}"
    console.print(formatted)
