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


@dataclass
class PortfolioUpdateEvent(BaseEvent):
    symbol: str
    quantity: float
    entry_price: float
    unrealized_pnl: float


@dataclass
class TradeClosedEvent(BaseEvent):
    symbol: str
    realized_pnl: float


@dataclass
class PerformanceUpdateEvent(BaseEvent):
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    drawdown_percent: float


@dataclass
class RiskViolationEvent(BaseEvent):
    reason: str
    severity: str


@dataclass
class RiskStatusEvent(BaseEvent):
    equity: float
    drawdown_percent: float
    daily_loss_percent: float
    status: str
