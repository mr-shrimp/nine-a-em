import random
import threading
import time

from app.core.event_bus import event_bus
from app.core.events import MarketDataEvent, OrderEvent, create_event
from app.core.logger import get_logger


class MockExchange:
    def __init__(self):
        self.logger = get_logger("mock_exchange")
        self.price = 50000.0
        self.running = False
        self.thread = None

    # --------------------------
    # Market Simulation
    # --------------------------

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._simulate_market)
        self.thread.start()

        self.logger.info("Mock exchange started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

        self.logger.warning("Mock exchange stopped")

    def _simulate_market(self):
        while self.running:
            # Simple random walk
            change = random.uniform(-50, 50)
            self.price += change

            event_bus.emit(
                create_event(
                    MarketDataEvent, symbol="BTCUSDT", price=round(self.price, 2)
                )
            )

            time.sleep(1)

    # --------------------------
    # Exchange Interface
    # --------------------------

    def get_price(self, symbol: str) -> float:
        return self.price

    def place_order(self, symbol: str, side: str, quantity: float):
        fill_price = self.price

        self.logger.info(
            "Order executed",
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=fill_price,
        )

        event_bus.emit(
            create_event(
                OrderEvent, symbol=symbol, side=side, quantity=quantity, status="FILLED"
            )
        )

        return {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": fill_price,
        }
