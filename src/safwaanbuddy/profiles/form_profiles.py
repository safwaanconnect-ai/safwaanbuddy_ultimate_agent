"""Structured form field definitions."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from ..core.config import ConfigManager


@dataclass
class FormProfile:
    """Form profile with field mappings."""
    
    name: str
    description: str = ""
    fields: Dict[str, str] = field(default_factory=dict)
    
    def get_field(self, key: str) -> Optional[str]:
        """Get field value."""
        return self.fields.get(key)
    
    def set_field(self, key: str, value: str) -> None:
        """Set field value."""
        self.fields[key] = value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "fields": self.fields
        }
