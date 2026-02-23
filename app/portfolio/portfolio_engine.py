from app.core.event_bus import event_bus
from app.core.events import OrderEvent, PortfolioUpdateEvent, create_event
from app.core.logger import get_logger


class PortfolioEngine:
    def __init__(self, exchange):
        self.logger = get_logger("portfolio")
        self.exchange = exchange

        # Minimal position state
        self.positions = {}  # symbol → dict

        # Subscribe to order fills
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
            # Open new position
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

            # If crossing zero, treat as close
            if old_qty != 0 and (old_qty > 0 > new_qty or old_qty < 0 < new_qty):
                self.logger.info("Position closed", symbol=symbol)
                new_qty = 0

            if new_qty == 0:
                position["quantity"] = 0
                position["entry_price"] = 0
            else:
                # Weighted average entry
                weighted_entry = (
                    (old_entry * abs(old_qty)) + (fill_price * quantity)
                ) / (abs(old_qty) + quantity)

                position["quantity"] = new_qty
                position["entry_price"] = weighted_entry

        self._emit_update(symbol)

    def _emit_update(self, symbol):

        position = self.positions.get(symbol)

        if not position:
            return

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
