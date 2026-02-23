from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def render_risk(state: dict):

    risk = state.get("risk", {})

    table = Table(expand=True)
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Equity", str(risk.get("equity", 0)))
    table.add_row("Drawdown %", str(risk.get("drawdown_percent", 0)))
    table.add_row("Daily Loss %", str(risk.get("daily_loss_percent", 0)))
    table.add_row("Max Drawdown %", str(risk.get("max_drawdown_limit", 0)))
    table.add_row("Max Daily Loss %", str(risk.get("max_daily_loss_limit", 0)))

    status = risk.get("status", "UNKNOWN")

    status_color = "green" if status == "OK" else "bold red"

    return Panel(
        table,
        title=Text(f"Risk Status: {status}", style=status_color),
        border_style=status_color,
    )
