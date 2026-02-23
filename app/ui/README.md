# Trading Bot - UI & Event Bus System

This document explains how the **Terminal UI system** and the **Event Bus architecture** work, how to use them, and how to extend them safely.

## Overview

The UI system is:

- Event-driven
- Decoupled from business logic
- Thread-safe
- Modular
- Expandable

The UI does **not** make trading decisions. It listens to domain events and renders system state.

### Architecture:

```
Strategy → EventBus → UI Subscriber → Terminal Screen
Risk → EventBus → UI Subscriber → Event Log Panel
Execution → EventBus → UI Subscriber → Event Log Panel
```

The UI reacts. It never controls logic.

## Directory Structure

```
app/
├── core/
│   ├── event_bus.py
│   ├── events.py
│
├── ui/
│   ├── screen_manager.py
│   ├── panels/
│   │   ├── header_panel.py
│   │   └── event_log_panel.py
```

## Event Bus

File:

```
app/core/event_bus.py
```

Purpose:

- Central communication hub
- Publishes and subscribes to domain events
- Decouples system components

### How it Works

The EventBus supports:

```python
event_bus.subscribe(EventType, handler)
event_bus.emit(event_instance)
```

When an event is emitted:

1. The bus finds all subscribers
2. Calls each handler
3. Handlers react accordingly

It is thread-safe.

### Example

```python
from app.core.event_bus import event_bus
from app.core.events import create_event, SystemEvent

event_bus.emit(
    create_event(
        SystemEvent,
        message="Application started",
        severity="INFO"
    )
)
```

No UI calls required.

## Event Definitions

File:

```
app/core/events.py
```

All events inherit from `BaseEvent`.

Example:

```python
@dataclass
class SystemEvent(BaseEvent):
    message: str
    severity: str = "INFO"
```

Other example events:

- SignalEvent
- OrderEvent
- RiskViolationEvent
- PositionClosedEvent

### Creating Events

Use:

```python
create_event(EventClass, **kwargs)
```

This automatically attaches:

- UUID
- Timestamp

Example:

```python
event_bus.emit(
    create_event(
        SignalEvent,
        symbol="BTCUSDT",
        signal_type="BUY",
        strategy_name="MovingAverage_v1"
    )
)
```

## Screen Manager

File:

```
app/ui/screen_manager.py
```

This is the terminal engine.

Responsibilities:

- Manage layout
- Refresh UI
- Subscribe to events
- Render panels
- Maintain UI state

### Starting the UI

In `main.py`:

```python
screen = ScreenManager(refresh_rate=0.5)

screen.update_state("app_name", settings.APP_NAME)
screen.update_state("environment", settings.ENVIRONMENT.value)
screen.update_state("status", "RUNNING")

screen.start()
```

`start()` runs the UI loop in the main thread.

## Header Panel

File:

```
app/ui/panels/header_panel.py
```

Renders:

- App name
- Environment
- Status

Uses values from:

```python
screen.update_status(key, value)
```

Example:

```python
screen.update_status("status", "ERROR")
```

## Event Log Panel

File:

```
app/ui/panels/event_log.py
```

Purpose:

- Real-time event display
- Debugging visibility
- Risk alerts
- Order activity monitoring

### Behaviour

- Keeps rolling buffer (deque)
- Thread-safe
- Displays last 10 visible events
- Color-coded severity

Severity styles:
| Level | Color |
| -------- | -------- |
| INFO | White |
| WARNING | Yellow |
| ERROR | Red |
| CRITICAL | Bold Red |

## How UI Connects to Event Bus

Inside `ScreenManager.__init__`:

```python
event_bus.subscribe(SystemEvent, self._handle_system_event)
event_bus.subscribe(SignalEvent, self._handle_signal_event)
event_bus.subscribe(OrderEvent, self._handle_order_event)
```

Each handler pushed events into the event log panel.

Example handler:

```python
def _handle_system_event(self, event: SystemEvent):
    self.event_log_panel.add_event(event.message, event.severity)
```

This is automatic. You do not call UI manually.

## How to Emit Event Properly

Correct way:

```
Business Logic → Emit Event
```

Wrong way:

```
Business Logic → Call screen.log_event()
```

Never couple trading logic to UI.

### Example: From Strategy

```python
event_bus.emit(
    create_event(
        SignalEvent,
        symbol="ETHUSDT",
        signal_type="SELL",
        strategy_name="MeanReversion_v2"
    )
)
```

UI updated automatically.

### Example: From Risk Engine

```python
event_bus.emit(
    create_event(
        SystemEvent,
        message="Daily loss threshold reached",
        severity="CRITICAL"
    )
)
```

Appears immediately in log panel.

## UI Deisng Rules (Important)

UI must NEVER:

- Query database
- Calculate PnL
- Call exchange APIs
- Make trading decisions
- Modify portfolio state

UI only renders.

## Extending the UI

To add a new panel:

1. Create new file in:
   ```
   app/ui/panels/
   ```
2. Add renderer function:
   ```python
   def render_my_panel(state):
       ...
   ```
3. Add layout region in `_create_layout()`
4. Update `_render()` to call it
5. Update `state` via event handlers

## Extending Event System

To add a new event type:

1. Define new dataclass in `events.py`
2. Emit event from domain logic.
3. Subscribe in `ScreenManager`
4. Add handler method

Example:

```python
@dataclass
class RiskViolationEvent(BaseEvent):
    reason: str
    severity: str
```

## Lifecycle Model

Application startup flow:

```
1. Load configuration
2. Initialize EventBus
3. Initialize ScreenManager
4. Subscribe UI to events
5. Start UI
6. Begin emitting events
```

Shutdown:

- Ctrl_C
- ScreenManager stops
- Application exists cleanly
