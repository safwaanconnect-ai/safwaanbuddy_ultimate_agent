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
        """Emits an event to all subscribers."""
        self._event_count += 1
        event_entry = {
            "id": self._event_count,
            "type": event_type,
            "data": data,
            "timestamp": time.time()
        }
        self._history.append(event_entry)
        
        # Keep history limited to prevent memory leak
        if len(self._history) > 2000:
            self._history.pop(0)

        if event_type in self._listeners:
            # Use a copy of the list to avoid issues if listeners unsubscribe during emission
            listeners_copy = list(self._listeners[event_type])
            for listener in listeners_copy:
                try:
                    # Check if listener is still valid or if it was removed
                    if listener in self._listeners[event_type]:
                        listener(data)
                except Exception as e:
                    import traceback
                    print(f"Error in event listener for {event_type}: {e}")
                    traceback.print_exc()

    def get_history(self, limit: int = 100):
        """Returns the last N events from history."""
        return self._history[-limit:]

    def clear_history(self):
        """Clears the event history."""
        self._history = []

    def get_stats(self):
        return {
            "total_events": self._event_count,
            "active_listeners": {etype: len(listeners) for etype, listeners in self._listeners.items()},
            "history_size": len(self._history)
        }

event_bus = EventBus()
