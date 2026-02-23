from app.core.config import settings
from app.core.event_bus import event_bus
from app.core.events import (
    PerformanceUpdateEvent,
    RiskStatusEvent,
    RiskViolationEvent,
    create_event,
)
from app.core.logger import get_logger


class RiskEngine:
    def __init__(self):
        self.logger = get_logger("risk")

        self.current_equity = 100000
        self.realized_pnl = 0
        self.drawdown_percent = 0

        event_bus.subscribe(PerformanceUpdateEvent, self._update_metrics)

    # --------------------------
    # Listen to performance updates
    # --------------------------

    def _update_metrics(self, event: PerformanceUpdateEvent):
        self.current_equity = event.equity
        self.realized_pnl = event.realized_pnl
        self.drawdown_percent = event.drawdown_percent
        self._emit_status()

    # --------------------------
    # Validate Order
    # --------------------------

    def validate_order(self, symbol: str, quantity: float, price: float) -> bool:

        position_value = abs(quantity * price)
        max_position_value = (
            settings.MAX_POSITION_SIZE_PERCENT / 100
        ) * self.current_equity

        # 1️⃣ Position size check
        if position_value > max_position_value:
            self._reject("Position size exceeds max % of equity")
            return False

        # 2️⃣ Drawdown check
        if self.drawdown_percent > settings.MAX_ACCOUNT_DRAWDOWN_PERCENT:
            self._reject("Max account drawdown exceeded")
            return False

        # 3️⃣ Daily loss check
        daily_loss_percent = (abs(self.realized_pnl) / self.current_equity) * 100

        if daily_loss_percent > settings.MAX_DAILY_LOSS_PERCENT:
            self._reject("Daily loss threshold exceeded")
            return False

        return True

    # --------------------------
    # Rejection Handler
    # --------------------------

    def _reject(self, reason: str):

        self.logger.warning("Risk rejection", reason=reason)

        event_bus.emit(
            create_event(
                RiskViolationEvent,
                reason=reason,
                severity="CRITICAL",
            )
        )

    def _emit_status(self):

        daily_loss_percent = (
            (abs(self.realized_pnl) / self.current_equity) * 100
            if self.current_equity > 0
            else 0
        )

        status = "OK"

        if self.drawdown_percent > settings.MAX_ACCOUNT_DRAWDOWN_PERCENT:
            status = "BLOCKED"
        elif daily_loss_percent > settings.MAX_DAILY_LOSS_PERCENT:
            status = "BLOCKED"

        event_bus.emit(
            create_event(
                RiskStatusEvent,
                equity=round(self.current_equity, 2),
                drawdown_percent=round(self.drawdown_percent, 2),
                daily_loss_percent=round(daily_loss_percent, 2),
                status=status,
            )
        )
