"""CRUD operations for user profiles with YAML storage."""

import logging
import yaml
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class ProfileManager:
    """Manage user profiles."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.profiles_dir = Path(self.config.get("profiles.data_dir", "data/profiles"))
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_profile: Optional[Dict] = None
    
    def create_profile(self, name: str, data: Dict[str, Any]) -> bool:
        """Create new profile.
        
        Args:
            name: Profile name
            data: Profile data
            
        Returns:
            True if successful
        """
        profile_file = self.profiles_dir / f"{name}.yaml"
        
        if profile_file.exists():
            self.logger.error(f"Profile already exists: {name}")
            return False
        
        profile = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **data
        }
        
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Created profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create profile: {e}")
            return False
    
    def load_profile(self, name: str) -> Optional[Dict]:
        """Load profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Profile data or None
        """
        profile_file = self.profiles_dir / f"{name}.yaml"
        
        if not profile_file.exists():
            self.logger.error(f"Profile not found: {name}")
            return None
        
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile = yaml.safe_load(f)
            
            self.current_profile = profile
            self.event_bus.emit(EventType.PROFILE_LOADED, {"name": name})
            self.logger.info(f"Loaded profile: {name}")
            return profile
        except Exception as e:
            self.logger.error(f"Failed to load profile: {e}")
            return None
    
    def save_profile(self, name: str, data: Dict[str, Any]) -> bool:
        """Save profile data.
        
        Args:
            name: Profile name
            data: Profile data to save
            
        Returns:
            True if successful
        """
        profile_file = self.profiles_dir / f"{name}.yaml"
        
        existing_data = {}
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    existing_data = yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.warning(f"Could not load existing profile: {e}")
        
        profile = {
            **existing_data,
            **data,
            "name": name,
            "updated_at": datetime.now().isoformat()
        }
        
        if "created_at" not in profile:
            profile["created_at"] = datetime.now().isoformat()
        
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
            
            self.event_bus.emit(EventType.PROFILE_SAVED, {"name": name})
            self.logger.info(f"Saved profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save profile: {e}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """Delete profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if successful
        """
        profile_file = self.profiles_dir / f"{name}.yaml"
        
        if not profile_file.exists():
            self.logger.error(f"Profile not found: {name}")
            return False
        
        try:
            profile_file.unlink()
            self.logger.info(f"Deleted profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete profile: {e}")
            return False
    
    def list_profiles(self) -> List[str]:
        """List all available profiles.
        
        Returns:
            List of profile names
        """
        profiles = []
        
        for profile_file in self.profiles_dir.glob("*.yaml"):
            profiles.append(profile_file.stem)
        
        return sorted(profiles)
    
    def export_profile(self, name: str, filepath: Path, format: str = "json") -> bool:
        """Export profile to file.
        
        Args:
            name: Profile name
            filepath: Output file path
            format: Export format (json, yaml)
            
        Returns:
            True if successful
        """
        profile = self.load_profile(name)
        
        if not profile:
            return False
        
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if format == "json":
                    json.dump(profile, f, indent=2)
                else:
                    yaml.dump(profile, f, default_flow_style=False)
            
            self.logger.info(f"Exported profile to: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export profile: {e}")
            return False
    
    def import_profile(self, filepath: Path, name: Optional[str] = None) -> bool:
        """Import profile from file.
        
        Args:
            filepath: Import file path
            name: Profile name (uses file name if None)
            
        Returns:
            True if successful
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            self.logger.error(f"File not found: {filepath}")
            return False
        
        if name is None:
            name = filepath.stem
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.suffix == '.json':
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
            
            return self.save_profile(name, data)
        except Exception as e:
            self.logger.error(f"Failed to import profile: {e}")
            return False
