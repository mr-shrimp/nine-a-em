from collections import deque
from datetime import datetime
from threading import Lock

from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class EventLogPanel:
    def __init__(self, max_events: int = 100):
        self.max_events = max_events
        self.events = deque(maxlen=max_events)
        self.lock = Lock()

    def add_event(self, message: str, severity: str = "INFO"):
        with self.lock:
            self.events.append(
                {
                    "time": datetime.utcnow().strftime("%H:%M:%S"),
                    "message": message,
                    "severity": severity.upper(),
                }
            )

    def render(self) -> Panel:
        table = Table.grid(expand=True)
        table.add_column("Time", width=10)
        table.add_column("Level", width=10)
        table.add_column("Message")

        severity_styles = {
            "INFO": "white",
            "WARNING": "yellow",
            "CRITICAL": "bold red",
            "ERROR": "red",
        }

        with self.lock:
            for event in list(self.events)[-10:]:
                style = severity_styles.get(event["severity"], "white")
                table.add_row(
                    event["time"],
                    Text(event["severity"], style=style),
                    Text(event["message"], style=style),
                )

        return Panel(table, title="Event Log", border_style="bright_magenta")
