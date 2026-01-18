import threading
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._listeners = defaultdict(list)
        return cls._instance

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable[[Any], None]):
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    def emit(self, event_type: str, data: Any = None):
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                # In a real system, we might want to run these in separate threads or async
                try:
                    listener(data)
                except Exception as e:
                    print(f"Error in event listener for {event_type}: {e}")

event_bus = EventBus()
