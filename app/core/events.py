from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4, UUID


@dataclass
class BaseEvent:
    event_id: UUID
    timestamp: datetime


def create_event(cls, **kwargs) -> BaseEvent:
    return cls(event_id=uuid4(), timestamp=datetime.utcnow(), **kwargs)


@dataclass
class SystemEvent(BaseEvent):
    message: str
    severity: str = "INFO"


@dataclass
class SignalEvent(BaseEvent):
    symbol: str
    signal_type: str
    strategy_name: str


@dataclass
class OrderEvent(BaseEvent):
    symbol: str
    side: str
    quantity: float
    status: str


@dataclass
class MarketDataEvent(BaseEvent):
    symbol: str
    price: float
