import random
import threading
import time

from app.core.config import settings
from app.core.event_bus import event_bus
from app.core.events import SystemEvent, create_event
from app.core.logger import get_logger
from app.exchange.mock_exchange import MockExchange


class ApplicationOrchestrator:
    def __init__(self, screen_manager):
        self.logger = get_logger("orchestrator")
        self.screen = screen_manager
        self.running = False
        self.thread = None
        self.exchange = MockExchange()

    def start(self):
        self.logger.info("Starting application orchestrator")

        self.exchange.start()

        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.start()

        event_bus.emit(
            create_event(
                SystemEvent, message="Application orchestrator started", severity="INFO"
            )
        )

    def stop(self):
        self.logger.warning("Stopping application orchestrator")
        self.running = False

        self.exchange.stop()

        if self.thread:
            self.thread.join()

        event_bus.emit(
            create_event(
                SystemEvent,
                message="Application orchestrator stopped",
                severity="WARNING",
            )
        )

    def _run_loop(self):
        self.logger.info("Main loop started")

        while self.running:
            try:
                self._heartbeat()
                time.sleep(settings.HEARTBEAT_INTERVAL_SECONDS)
            except Exception as e:
                self.logger.error("Unhandled error in main loop", error=str(e))

        self.logger.info("Main loop exited")

    def _heartbeat(self):
        price = self.exchange.get_price("BTCUSDT")

        if random.random() < 0.3:  # 30% chance to place order
            side = random.choice(["BUY", "SELL"])
            quantity = round(random.uniform(0.01, 0.1), 4)

            self.exchange.place_order("BTCUSDT", side, quantity)

        event_bus.emit(
            create_event(
                SystemEvent,
                message=f"Heartbeat OK | Price: {round(price, 2)}",
                severity="INFO",
            )
        )
