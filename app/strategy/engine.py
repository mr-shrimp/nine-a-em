from typing import List
from app.core.event_bus import event_bus
from app.core.events import MarketDataEvent
from app.core.logger import get_logger
from app.strategy.base import BaseStrategy


class StrategyEngine:
    def __init__(self):
        self.logger = get_logger("strategy_engine")
        self.strategies: List[BaseStrategy] = []

        event_bus.subscribe(MarketDataEvent, self._on_market_data)

    def register(self, strategy: BaseStrategy):
        self.logger.info("Strategy registered", strategy=strategy.name)
        self.strategies.append(strategy)

    def _on_market_data(self, event: MarketDataEvent):
        for strategy in self.strategies:
            try:
                strategy.on_market_data(event)
            except Exception as e:
                self.logger.error(
                    "Strategy error", strategy=strategy.name, error=str(e)
                )
