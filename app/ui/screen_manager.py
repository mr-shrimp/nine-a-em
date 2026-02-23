from time import sleep
from typing import Any, Dict

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

from app.core.event_bus import event_bus
from app.core.events import (
    MarketDataEvent,
    OrderEvent,
    PortfolioUpdateEvent,
    SignalEvent,
    SystemEvent,
)
from app.ui.panels.event_log_panel import EventLogPanel
from app.ui.panels.header_panel import render_header
from app.ui.panels.market_panel import render_market
from app.ui.panels.positions_panel import render_positions


class ScreenManager:
    def __init__(self, refresh_rate: float = 1.0):
        self.console = Console()
        self.refresh_rate = refresh_rate
        self.layout = self._create_layout()
        self.state: Dict[str, Any] = {}
        self.running = False
        self.event_log_panel = EventLogPanel(max_events=200)

        event_bus.subscribe(SystemEvent, self._handle_system_event)
        event_bus.subscribe(SignalEvent, self._handle_signal_event)
        event_bus.subscribe(OrderEvent, self._handle_order_event)
        event_bus.subscribe(MarketDataEvent, self._handle_market_data)
        event_bus.subscribe(PortfolioUpdateEvent, self._handle_portfolio_update)

    def _create_layout(self) -> Layout:
        layout = Layout()

        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="event_log", size=12),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        layout["left"].split(
            Layout(name="market"),
            Layout(name="performance"),
        )

        layout["right"].split(
            Layout(name="positions"),
            Layout(name="risk"),
        )

        return layout

    def start(self):
        self.running = True
        self._run()

    def stop(self):
        self.running = False

    def _run(self):
        with Live(self.layout, refresh_per_second=4, screen=True):
            while self.running:
                self._render()
                sleep(self.refresh_rate)

    def _render(self):
        self.layout["header"].update(render_header(self.state))
        self.layout["market"].update(render_market(self.state))
        self.layout["positions"].update(render_positions(self.state))
        self.layout["performance"].update(Panel("Performance loading..."))
        self.layout["risk"].update(Panel("Risk engine ready."))
        self.layout["event_log"].update(self.event_log_panel.render())
        self.layout["footer"].update(Panel("Press Ctrl+C to exit"))

    def update_state(self, key: str, value: Any):
        self.state[key] = value

    def log_event(self, message: str, severity: str = "INFO"):
        self.event_log_panel.add_event(message, severity)

    def _handle_system_event(self, event: SystemEvent):
        self.event_log_panel.add_event(event.message, event.severity)

    def _handle_signal_event(self, event: SignalEvent):
        message = f"{event.strategy_name} → {event.signal_type} {event.symbol}"
        self.event_log_panel.add_event(message, "INFO")

    def _handle_order_event(self, event: OrderEvent):
        message = f"{event.status} {event.side} {event.quantity} {event.symbol}"
        self.event_log_panel.add_event(
            message, "WARNING" if event.status == "REJECTED" else "INFO"
        )

    def _handle_market_data(self, event: MarketDataEvent):
        self.state["symbol"] = event.symbol
        self.state["price"] = event.price

    def _handle_portfolio_update(self, event: PortfolioUpdateEvent):
        positions = self.state.setdefault("positions", {})
        positions[event.symbol] = {
            "quantity": event.quantity,
            "entry_price": event.entry_price,
            "unrealized_pnl": event.unrealized_pnl,
        }
