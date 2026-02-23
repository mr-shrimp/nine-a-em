from collections import deque
from statistics import mean

from app.core.event_bus import event_bus
from app.core.events import SignalEvent, create_event
from app.strategy.base import BaseStrategy


class SMAStrategy(BaseStrategy):
    def __init__(self, symbol: str, short_window: int, long_window: int):
        super().__init__(name=f"SMA_{short_window}_{long_window}")

        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window

        self.prices = deque(maxlen=long_window)
        self.last_signal = None

    def on_market_data(self, event):

        if event.symbol != self.symbol:
            return

        self.prices.append(event.price)

        if len(self.prices) < self.long_window:
            return

        short_ma = mean(list(self.prices)[-self.short_window :])
        long_ma = mean(self.prices)

        if short_ma > long_ma and self.last_signal != "BUY":
            self._emit_signal("BUY")
            self.last_signal = "BUY"

        elif short_ma < long_ma and self.last_signal != "SELL":
            self._emit_signal("SELL")
            self.last_signal = "SELL"

    def _emit_signal(self, signal_type):

        event_bus.emit(
            create_event(
                SignalEvent,
                symbol=self.symbol,
                signal_type=signal_type,
                strategy_name=self.name,
            )
        )
