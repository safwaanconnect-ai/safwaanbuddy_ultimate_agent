"""
SafwaanBuddy Ultimate++ v7.0
A comprehensive Windows AI assistant with voice control and automation.
"""

__version__ = "7.0.0"
__author__ = "SafwaanBuddy Team"

from .core.events import EventBus
from .core.config import ConfigManager
from .core.logger import setup_logger

__all__ = ["EventBus", "ConfigManager", "setup_logger", "__version__"]
