"""Alert and notification system."""

import logging
from typing import Optional
from enum import Enum

from ..core.events import EventBus, EventType


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSystem:
    """Manage alerts and notifications."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_bus = EventBus()
    
    def send_alert(self, message: str, level: AlertLevel = AlertLevel.INFO, title: Optional[str] = None) -> None:
        """Send alert.
        
        Args:
            message: Alert message
            level: Alert level
            title: Alert title
        """
        event_type_map = {
            AlertLevel.INFO: EventType.INFO_MESSAGE,
            AlertLevel.WARNING: EventType.WARNING_ISSUED,
            AlertLevel.ERROR: EventType.ERROR_OCCURRED,
            AlertLevel.CRITICAL: EventType.ERROR_OCCURRED
        }
        
        event_type = event_type_map.get(level, EventType.INFO_MESSAGE)
        
        self.event_bus.emit(event_type, {
            "message": message,
            "title": title or level.value.capitalize(),
            "level": level.value
        })
        
        log_method = {
            AlertLevel.INFO: self.logger.info,
            AlertLevel.WARNING: self.logger.warning,
            AlertLevel.ERROR: self.logger.error,
            AlertLevel.CRITICAL: self.logger.critical
        }.get(level, self.logger.info)
        
        log_method(f"Alert: {message}")
