from collections import defaultdict
from threading import Lock
from typing import Callable, Type, Dict, List


class EventBus:
    def __init__(self):
        self._subscribers: Dict[Type, List[Callable]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, event_type: Type, handler: Callable):
        with self._lock:
            self._subscribers[event_type].append(handler)

    def emit(self, event):
        handlers = []

        with self._lock:
            for event_type, subs in self._subscribers.items():
                if isinstance(event, event_type):
                    handlers.extend(subs)

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Never allow UI crash from event handler
                print(f"Event handler error: {e}")


event_bus = EventBus()
