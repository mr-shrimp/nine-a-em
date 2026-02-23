from rich.panel import Panel
from rich.table import Table


def render_positions(state: dict):

    table = Table(title="Positions", expand=True)
    table.add_column("Symbol")
    table.add_column("Qty")
    table.add_column("Entry")
    table.add_column("Unrealized PnL")

    positions = state.get("positions", {})

    for symbol, data in positions.items():
        table.add_row(
            symbol,
            str(round(data["quantity"], 4)),
            str(data["entry_price"]),
            str(data["unrealized_pnl"]),
        )

    return Panel(table, border_style="bright_cyan")
