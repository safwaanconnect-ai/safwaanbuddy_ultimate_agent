import threading
from collections import defaultdict
from typing import Callable, Any
import time

class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._listeners = defaultdict(list)
                cls._instance._history = []
                cls._instance._event_count = 0
        return cls._instance

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        self._listeners[event_type].append(listener)
        return len(self._listeners[event_type]) # Mock subscription ID

    def unsubscribe(self, event_type: str, listener: Callable[[Any], None]):
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
            except ValueError:
                pass

    def emit(self, event_type: str, data: Any = None):
        self._event_count += 1
        self._history.append({"type": event_type, "data": data, "timestamp": time.time()})
        if len(self._history) > 1000:
            self._history.pop(0)

        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    listener(data)
                except Exception as e:
                    print(f"Error in event listener for {event_type}: {e}")

    def get_stats(self):
        return {
            "total_events": self._event_count,
            "active_listeners": {etype: len(listeners) for etype, listeners in self._listeners.items()},
            "history_size": len(self._history)
        }

event_bus = EventBus()
