from rich.align import Align
from rich.panel import Panel
from rich.text import Text

STATUS_STYLES = {
    "RUNNING": "bold green",
    "STOPPED": "bold red",
    "ERROR": "bold red",
    "INITIALIZING": "bold yellow",
}


def render_header(state: dict) -> Panel:

    app_name = state.get("app_name", "TradingBot")
    environment = state.get("environment", "DEV")
    status = state.get("status", "INITIALIZING")

    style = STATUS_STYLES.get(status, "bold white")

    header_text = Text.assemble(
        (f"{app_name}", "bold white"),
        (" | ", "white"),
        (f"ENV: {environment}", "bold cyan"),
        (" | ", "white"),
        (f"STATUS: {status}", style),
    )

    return Panel(Align.center(header_text), border_style="bright_blue")
