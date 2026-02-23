from app.core.event_bus import event_bus
from app.core.events import SignalEvent
from app.core.logger import get_logger


class ExecutionEngine:
    def __init__(self, exchange, risk_engine):
        self.logger = get_logger("execution")
        self.exchange = exchange
        self.risk = risk_engine

        event_bus.subscribe(SignalEvent, self._handle_signal)

    def _handle_signal(self, event: SignalEvent):

        side = event.signal_type
        quantity = 0.005  # fixed size for now
        price = self.exchange.get_price(event.symbol)

        approved = self.risk.validate_order(event.symbol, quantity, price)

        if approved:
            self.exchange.place_order(event.symbol, side, quantity)
        else:
            self.logger.warning(
                "Signal rejected by risk", symbol=event.symbol, side=side
            )
