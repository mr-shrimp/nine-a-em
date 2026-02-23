from abc import ABC, abstractmethod


class BaseExchange(ABC):
    @abstractmethod
    def get_price(self, symbol: str) -> float:
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: float) -> dict:
        pass
