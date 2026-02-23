from rich.panel import Panel
from rich.text import Text


def render_market(state: dict):
    symbol = state.get("symbol", "N/A")
    price = state.get("price", "N/A")

    content = Text.assemble(
        ("Symbol: ", "bold white"),
        (f"{symbol}\n", "cyan"),
        ("Price: ", "bold white"),
        (f"{price}", "green"),
    )

    return Panel(content, title="Market Data", border_style="bright_green")
