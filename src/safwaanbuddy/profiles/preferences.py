"""User settings and interface preferences."""

import logging
from pathlib import Path
from typing import Any, Dict
import yaml

from ..core.config import ConfigManager


class Preferences:
    """Manage user preferences."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        self.prefs_file = Path("data/preferences.yaml")
        self.preferences: Dict[str, Any] = {}
        
        self.load()
    
    def load(self) -> None:
        """Load preferences from file."""
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    self.preferences = yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.error(f"Failed to load preferences: {e}")
    
    def save(self) -> bool:
        """Save preferences to file."""
        try:
            self.prefs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.preferences, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get preference value."""
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set preference value."""
        self.preferences[key] = value
        self.save()
