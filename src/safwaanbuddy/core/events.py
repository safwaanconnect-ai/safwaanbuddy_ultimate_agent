"""Event bus system for inter-module communication."""

import logging
from typing import Callable, Dict, List, Any
from threading import Lock
from enum import Enum


class EventType(Enum):
    """Standard event types."""
    
    VOICE_COMMAND = "voice_command"
    SPEECH_DETECTED = "speech_detected"
    WAKE_WORD_DETECTED = "wake_word_detected"
    TTS_STARTED = "tts_started"
    TTS_FINISHED = "tts_finished"
    
    AUTOMATION_STARTED = "automation_started"
    AUTOMATION_COMPLETED = "automation_completed"
    AUTOMATION_FAILED = "automation_failed"
    CLICK_PERFORMED = "click_performed"
    TYPE_PERFORMED = "type_performed"
    
    FORM_FILL_STARTED = "form_fill_started"
    FORM_FILL_COMPLETED = "form_fill_completed"
    
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_RECORDED = "workflow_recorded"
    
    BROWSER_OPENED = "browser_opened"
    BROWSER_CLOSED = "browser_closed"
    PAGE_LOADED = "page_loaded"
    SEARCH_PERFORMED = "search_performed"
    
    DOCUMENT_GENERATED = "document_generated"
    DOCUMENT_SAVED = "document_saved"
    
    PROFILE_LOADED = "profile_loaded"
    PROFILE_SAVED = "profile_saved"
    
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_EXECUTED = "plugin_executed"
    
    UI_SHOWN = "ui_shown"
    UI_HIDDEN = "ui_hidden"
    OVERLAY_SHOWN = "overlay_shown"
    OVERLAY_HIDDEN = "overlay_hidden"
    
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"
    INFO_MESSAGE = "info_message"
    
    SYSTEM_STARTED = "system_started"
    SYSTEM_SHUTDOWN = "system_shutdown"


class Event:
    """Event container."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.type = event_type
        self.data = data or {}
    
    def __repr__(self):
        return f"Event(type={self.type.value}, data={self.data})"


class EventBus:
    """Central event bus for application-wide communication."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._logger = logging.getLogger(__name__)
        self._initialized = True
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            self._logger.debug(f"Subscribed to {event_type.value}: {callback.__name__}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                self._logger.debug(f"Unsubscribed from {event_type.value}: {callback.__name__}")
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None) -> None:
        """Emit an event to all subscribers."""
        event = Event(event_type, data)
        
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self._logger.error(f"Error in event handler {callback.__name__}: {e}", exc_info=True)
    
    def clear(self) -> None:
        """Clear all subscriptions."""
        self._subscribers.clear()
        self._logger.info("Event bus cleared")
