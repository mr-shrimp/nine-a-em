from abc import ABC, abstractmethod
from app.core.events import MarketDataEvent


class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def on_market_data(self, event: MarketDataEvent):
        """
        Called whenever new market data arrives.
        Strategy decides whether to emit a signal.
        """
        pass
