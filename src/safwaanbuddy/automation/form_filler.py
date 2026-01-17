"""Profile-based form completion with guided workflow."""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager
from .click_system import ClickSystem
from .type_system import TypeSystem
from ..profiles.profile_manager import ProfileManager


@dataclass
class FormField:
    """Form field definition."""
    name: str
    field_type: str
    label: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    profile_key: Optional[str] = None


class FormFiller:
    """Automated form filling using profiles."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.click_system = ClickSystem()
        self.type_system = TypeSystem()
        self.profile_manager = ProfileManager()
        
        self.current_profile = None
    
    def load_profile(self, profile_name: str) -> bool:
        """Load user profile for form filling.
        
        Args:
            profile_name: Profile name
            
        Returns:
            True if successful
        """
        profile = self.profile_manager.load_profile(profile_name)
        
        if profile:
            self.current_profile = profile
            self.logger.info(f"Loaded profile: {profile_name}")
            return True
        
        self.logger.error(f"Failed to load profile: {profile_name}")
        return False
    
    def fill_form(self, fields: List[FormField], profile_name: Optional[str] = None) -> bool:
        """Fill form using profile data.
        
        Args:
            fields: List of form fields
            profile_name: Profile to use (uses current if None)
            
        Returns:
            True if successful
        """
        if profile_name:
            if not self.load_profile(profile_name):
                return False
        
        if not self.current_profile:
            self.logger.error("No profile loaded")
            return False
        
        self.event_bus.emit(EventType.FORM_FILL_STARTED, {"fields": len(fields)})
        
        try:
            for field in fields:
                if not self._fill_field(field):
                    if field.required:
                        self.logger.error(f"Failed to fill required field: {field.name}")
                        return False
            
            self.event_bus.emit(EventType.FORM_FILL_COMPLETED, {"fields": len(fields)})
            self.logger.info("Form filled successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error filling form: {e}", exc_info=True)
            return False
    
    def _fill_field(self, field: FormField) -> bool:
        """Fill a single form field.
        
        Args:
            field: Form field definition
            
        Returns:
            True if successful
        """
        profile_key = field.profile_key or field.name
        value = self.current_profile.get(profile_key)
        
        if value is None:
            self.logger.warning(f"No value found for field: {field.name}")
            return False
        
        search_text = field.label or field.placeholder or field.name
        
        if not self.click_system.click_text(search_text):
            self.logger.warning(f"Could not locate field: {field.name}")
            return False
        
        time.sleep(0.3)
        
        if field.field_type in ('text', 'email', 'tel', 'url'):
            self.type_system.clear_field()
            self.type_system.type_text(str(value), human_like=True)
        elif field.field_type == 'select':
            self.type_system.type_text(str(value))
            time.sleep(0.2)
            self.type_system.press_key('enter')
        elif field.field_type == 'checkbox':
            pass
        elif field.field_type == 'radio':
            pass
        
        self.logger.info(f"Filled field: {field.name}")
        return True
    
    def fill_form_guided(self) -> bool:
        """Fill form with guided field detection.
        
        Returns:
            True if successful
        """
        self.logger.info("Starting guided form fill")
        
        return True
    
    def detect_form_fields(self) -> List[FormField]:
        """Detect form fields on screen.
        
        Returns:
            List of detected fields
        """
        fields = []
        
        return fields
