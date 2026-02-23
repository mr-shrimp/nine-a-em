from app.core.event_bus import event_bus
from app.core.events import (
    OrderEvent,
    PerformanceUpdateEvent,
    PortfolioUpdateEvent,
    TradeClosedEvent,
    create_event,
)
from app.core.logger import get_logger


class PortfolioEngine:
    def __init__(self, exchange):
        self.logger = get_logger("portfolio")
        self.exchange = exchange

        self.positions = {}
        self.realized_pnl_total = 0.0
        self.starting_balance = 100000.0
        self.equity = self.starting_balance
        self.peak_equity = self.starting_balance

        event_bus.subscribe(OrderEvent, self._handle_order)

    def _handle_order(self, event: OrderEvent):

        if event.status != "FILLED":
            return

        symbol = event.symbol
        side = event.side
        quantity = event.quantity
        fill_price = self.exchange.get_price(symbol)

        position = self.positions.get(symbol)

        if not position:
            self.positions[symbol] = {
                "quantity": quantity if side == "BUY" else -quantity,
                "entry_price": fill_price,
            }

        else:
            old_qty = position["quantity"]
            old_entry = position["entry_price"]

            if side == "BUY":
                new_qty = old_qty + quantity
            else:
                new_qty = old_qty - quantity

            # Position closing logic
            if old_qty > 0 and new_qty <= 0:
                realized = (fill_price - old_entry) * abs(old_qty)
                self._close_position(symbol, realized)
                return

            elif old_qty < 0 and new_qty >= 0:
                realized = (old_entry - fill_price) * abs(old_qty)
                self._close_position(symbol, realized)
                return

            # Otherwise scale position
            weighted_entry = ((old_entry * abs(old_qty)) + (fill_price * quantity)) / (
                abs(old_qty) + quantity
            )

            position["quantity"] = new_qty
            position["entry_price"] = weighted_entry

        self._emit_portfolio_update(symbol)

    def _close_position(self, symbol, realized):

        self.logger.info("Trade closed", symbol=symbol, realized_pnl=realized)

        self.realized_pnl_total += realized
        self.positions[symbol] = {"quantity": 0, "entry_price": 0}

        event_bus.emit(
            create_event(
                TradeClosedEvent,
                symbol=symbol,
                realized_pnl=round(realized, 2),
            )
        )

        self._emit_performance_update()

    def _emit_portfolio_update(self, symbol):

        position = self.positions.get(symbol)
        quantity = position["quantity"]
        entry_price = position["entry_price"]

        if quantity == 0:
            unrealized = 0
        else:
            current_price = self.exchange.get_price(symbol)

            if quantity > 0:
                unrealized = (current_price - entry_price) * quantity
            else:
                unrealized = (entry_price - current_price) * abs(quantity)

        event_bus.emit(
            create_event(
                PortfolioUpdateEvent,
                symbol=symbol,
                quantity=quantity,
                entry_price=round(entry_price, 2),
                unrealized_pnl=round(unrealized, 2),
            )
        )

        self._emit_performance_update()

    def _emit_performance_update(self):

        total_unrealized = 0

        for symbol, pos in self.positions.items():
            qty = pos["quantity"]
            entry = pos["entry_price"]

            if qty == 0:
                continue

            current_price = self.exchange.get_price(symbol)

            if qty > 0:
                total_unrealized += (current_price - entry) * qty
            else:
                total_unrealized += (entry - current_price) * abs(qty)

        self.equity = self.starting_balance + self.realized_pnl_total + total_unrealized

        if self.equity > self.peak_equity:
            self.peak_equity = self.equity

        drawdown = ((self.peak_equity - self.equity) / self.peak_equity) * 100

        event_bus.emit(
            create_event(
                PerformanceUpdateEvent,
                equity=round(self.equity, 2),
                realized_pnl=round(self.realized_pnl_total, 2),
                unrealized_pnl=round(total_unrealized, 2),
                drawdown_percent=round(drawdown, 2),
            )
        )
