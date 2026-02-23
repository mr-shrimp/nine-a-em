from rich.panel import Panel
from rich.table import Table


def render_performance(state: dict):

    table = Table(expand=True)
    table.add_column("Metric")
    table.add_column("Value")

    perf = state.get("performance", {})

    table.add_row("Equity", str(perf.get("equity", 0)))
    table.add_row("Realized PnL", str(perf.get("realized_pnl", 0)))
    table.add_row("Unrealized PnL", str(perf.get("unrealized_pnl", 0)))
    table.add_row("Drawdown %", str(perf.get("drawdown_percent", 0)))

    return Panel(table, title="Performance", border_style="bright_yellow")
