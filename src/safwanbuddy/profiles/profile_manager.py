#!/usr/bin/env python3
"""
Profile Manager for SafwanBuddy
Manages user profiles and personal information for form filling and automation
"""

import logging
import yaml
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PersonalInfo:
    """Personal information structure"""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    mobile: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "United States"
    date_of_birth: str = ""
    gender: str = ""
    ssn: str = ""
    
    def __post_init__(self):
        """Generate full name if not provided"""
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name} {self.last_name}".strip()

@dataclass
class WorkInfo:
    """Work-related information"""
    company: str = ""
    job_title: str = ""
    department: str = ""
    work_email: str = ""
    work_phone: str = ""
    work_address: str = ""
    manager_name: str = ""
    employee_id: str = ""
    
@dataclass
class ContactInfo:
    """Contact information for various services"""
    emergency_contact: str = ""
    emergency_phone: str = ""
    preferred_contact: str = ""  # email, phone, mobile
    timezone: str = "UTC"
    language: str = "en"
    
@dataclass
class FinancialInfo:
    """Financial information"""
    bank_name: str = ""
    account_number: str = ""
    routing_number: str = ""
    credit_card_number: str = ""
    expiry_date: str = ""
    cvv: str = ""
    
    def mask_sensitive_info(self):
        """Mask sensitive information for logging"""
        masked = asdict(self)
        if masked.get('account_number'):
            masked['account_number'] = "*" * (len(masked['account_number']) - 4) + masked['account_number'][-4:]
        if masked.get('credit_card_number'):
            masked['credit_card_number'] = "*" * (len(masked['credit_card_number']) - 4) + masked['credit_card_number'][-4:]
        return masked

@dataclass
class Preferences:
    """User preferences and settings"""
    preferred_browser: str = "chrome"
    default_language: str = "en"
    email_signature: str = ""
    auto_fill_enabled: bool = True
    voice_feedback: bool = True
    confirm_actions: bool = True
    
@dataclass
class UserProfile:
    """Complete user profile"""
    id: str
    name: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    # Profile data sections
    personal: PersonalInfo = field(default_factory=PersonalInfo)
    work: WorkInfo = field(default_factory=WorkInfo)
    contact: ContactInfo = field(default_factory=ContactInfo)
    financial: FinancialInfo = field(default_factory=FinancialInfo)
    preferences: Preferences = field(default_factory=Preferences)
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    auto_fill_fields: Dict[str, str] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get profile value using dot notation
        
        Args:
            key: Key in format 'section.field' (e.g., 'personal.email')
            default: Default value if key not found
            
        Returns:
            Profile value or default
        """
        try:
            keys = key.split('.')
            obj = self
            
            for k in keys:
                if hasattr(obj, k):
                    obj = getattr(obj, k)
                elif isinstance(obj, dict) and k in obj:
                    obj = obj[k]
                else:
                    return default
            
            return obj
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set profile value using dot notation
        
        Args:
            key: Key in format 'section.field'
            value: Value to set
            
        Returns:
            bool: True if set successfully
        """
        try:
            keys = key.split('.')
            obj = self
            
            # Navigate to parent object
            for k in keys[:-1]:
                if hasattr(obj, k):
                    obj = getattr(obj, k)
                elif isinstance(obj, dict):
                    if k not in obj:
                        obj[k] = {}
                    obj = obj[k]
                else:
                    return False
            
            # Set the value
            final_key = keys[-1]
            if hasattr(obj, final_key):
                setattr(obj, final_key, value)
                self.modified = datetime.now()
                return True
            elif isinstance(obj, dict):
                obj[final_key] = value
                self.modified = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to set profile key '{key}': {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        data = asdict(self)
        # Convert datetime objects to strings
        if 'created' in data:
            data['created'] = data['created'].isoformat() if isinstance(data['created'], datetime) else data['created']
        if 'modified' in data:
            data['modified'] = data['modified'].isoformat() if isinstance(data['modified'], datetime) else data['modified']
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> bool:
        """
        Load profile from dictionary
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            # Handle datetime fields
            for field_name in ['created', 'modified']:
                if field_name in data and isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
            
            # Update profile attributes
            for key, value in data.items():
                if hasattr(self, key):
                    if key in ['personal', 'work', 'contact', 'financial', 'preferences']:
                        # Handle nested dataclasses
                        section_obj = getattr(self, key)
                        if hasattr(section_obj, '__dataclass_fields__'):
                            for field_name, field_value in value.items():
                                if hasattr(section_obj, field_name):
                                    setattr(section_obj, field_name, field_value)
                    else:
                        setattr(self, key, value)
            
            self.modified = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Failed to load profile from dict: {e}")
            return False
    
    def validate(self) -> List[str]:
        """
        Validate profile data
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        if not self.id:
            errors.append("Profile ID is required")
        
        if not self.name:
            errors.append("Profile name is required")
        
        # Validate email formats
        if self.personal.email and '@' not in self.personal.email:
            errors.append("Personal email format is invalid")
        
        if self.work.work_email and '@' not in self.work.work_email:
            errors.append("Work email format is invalid")
        
        # Validate phone numbers (basic check)
        if self.personal.phone and len(self.personal.phone) < 10:
            errors.append("Personal phone number seems too short")
        
        # Check for potential security issues
        if self.financial.ssn and len(self.financial.ssn.replace('-', '').replace(' ', '')) != 9:
            errors.append("SSN format appears invalid")
        
        return errors
    
    def mask_sensitive_data(self) -> 'UserProfile':
        """Create a copy with sensitive data masked"""
        masked_profile = UserProfile(
            id=self.id,
            name=self.name,
            created=self.created,
            modified=self.modified,
            is_active=self.is_active,
            personal=self.personal,
            work=self.work,
            contact=self.contact,
            financial=self.financial.__class__(**self.financial.__dict__),
            preferences=self.preferences,
            tags=self.tags.copy(),
            notes=self.notes,
            auto_fill_fields=self.auto_fill_fields.copy()
        )
        
        # Mask sensitive financial information
        masked_profile.financial = masked_profile.financial.mask_sensitive_info()
        
        return masked_profile

class ProfileManager:
    """Manages user profiles for SafwanBuddy"""
    
    def __init__(self, config_manager=None):
        """
        Initialize Profile Manager
        
        Args:
            config_manager: Configuration manager for settings
        """
        self.config_manager = config_manager
        self.profiles_dir = Path("profiles")
        self.active_profile_id = None
        self.profiles: Dict[str, UserProfile] = {}
        self.auto_save = True
        
        # Ensure profiles directory exists
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Load profiles
        self._load_profiles()
        
        # Load active profile from config
        self._load_active_profile()
        
        logger.info(f"Profile Manager initialized with {len(self.profiles)} profiles")
    
    def _load_profiles(self):
        """Load all profiles from directory"""
        try:
            for profile_file in self.profiles_dir.glob("*.yaml"):
                try:
                    profile = self.load_profile_file(str(profile_file))
                    if profile:
                        self.profiles[profile.id] = profile
                        logger.debug(f"Loaded profile: {profile.name}")
                except Exception as e:
                    logger.error(f"Failed to load profile {profile_file}: {e}")
            
            logger.info(f"Loaded {len(self.profiles)} profiles")
            
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
    
    def _load_active_profile(self):
        """Load active profile from configuration"""
        try:
            if self.config_manager:
                active_id = self.config_manager.get('profile.active_profile')
                if active_id and active_id in self.profiles:
                    self.active_profile_id = active_id
                    logger.info(f"Active profile set to: {active_id}")
        except Exception as e:
            logger.warning(f"Failed to load active profile: {e}")
    
    def create_profile(self, name: str, profile_id: str = None) -> UserProfile:
        """
        Create a new profile
        
        Args:
            name: Profile name
            profile_id: Optional profile ID (auto-generated if None)
            
        Returns:
            UserProfile: Created profile
        """
        try:
            # Generate ID if not provided
            if not profile_id:
                profile_id = self._generate_profile_id(name)
            
            # Check if ID already exists
            if profile_id in self.profiles:
                raise ValueError(f"Profile ID '{profile_id}' already exists")
            
            # Create profile
            profile = UserProfile(id=profile_id, name=name)
            
            # Save profile
            if self.save_profile(profile):
                self.profiles[profile_id] = profile
                
                # Set as active if it's the first profile
                if not self.active_profile_id:
                    self.set_active_profile(profile_id)
                
                logger.info(f"Created profile: {name} ({profile_id})")
                return profile
            else:
                raise Exception("Failed to save profile")
                
        except Exception as e:
            logger.error(f"Failed to create profile '{name}': {e}")
            raise
    
    def load_profile(self, profile_id: str) -> Optional[UserProfile]:
        """
        Load a profile by ID
        
        Args:
            profile_id: Profile ID to load
            
        Returns:
            UserProfile or None if not found
        """
        try:
            if profile_id in self.profiles:
                return self.profiles[profile_id]
            
            # Try to load from file
            profile_file = self.profiles_dir / f"{profile_id}.yaml"
            if profile_file.exists():
                profile = self.load_profile_file(str(profile_file))
                if profile:
                    self.profiles[profile_id] = profile
                    return profile
            
            logger.warning(f"Profile not found: {profile_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load profile '{profile_id}': {e}")
            return None
    
    def load_profile_file(self, file_path: str) -> Optional[UserProfile]:
        """
        Load profile from YAML file
        
        Args:
            file_path: Path to profile YAML file
            
        Returns:
            UserProfile or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning(f"Empty profile file: {file_path}")
                return None
            
            # Create profile object
            profile = UserProfile(
                id=data.get('id', ''),
                name=data.get('name', ''),
                is_active=data.get('is_active', True),
                tags=data.get('tags', []),
                notes=data.get('notes', ''),
                auto_fill_fields=data.get('auto_fill_fields', {})
            )
            
            # Load nested objects
            if 'personal' in data:
                profile.personal = PersonalInfo(**data['personal'])
            
            if 'work' in data:
                profile.work = WorkInfo(**data['work'])
            
            if 'contact' in data:
                profile.contact = ContactInfo(**data['contact'])
            
            if 'financial' in data:
                profile.financial = FinancialInfo(**data['financial'])
            
            if 'preferences' in data:
                profile.preferences = Preferences(**data['preferences'])
            
            # Load dates
            if 'created' in data and data['created']:
                if isinstance(data['created'], str):
                    profile.created = datetime.fromisoformat(data['created'])
                else:
                    profile.created = data['created']
            
            if 'modified' in data and data['modified']:
                if isinstance(data['modified'], str):
                    profile.modified = datetime.fromisoformat(data['modified'])
                else:
                    profile.modified = data['modified']
            
            # Validate profile
            errors = profile.validate()
            if errors:
                logger.warning(f"Profile validation errors: {errors}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to load profile from {file_path}: {e}")
            return None
    
    def save_profile(self, profile: UserProfile) -> bool:
        """
        Save profile to file
        
        Args:
            profile: Profile to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Validate before saving
            errors = profile.validate()
            if errors:
                logger.warning(f"Profile has validation errors: {errors}")
            
            # Update modified timestamp
            profile.modified = datetime.now()
            
            # Create file path
            profile_file = self.profiles_dir / f"{profile.id}.yaml"
            
            # Convert to dict
            profile_dict = profile.to_dict()
            
            # Save to file
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(profile_dict, f, default_flow_style=False, indent=2, allow_unicode=True)
            
            logger.debug(f"Saved profile: {profile.name} ({profile.id})")
            
            # Update in-memory cache
            self.profiles[profile.id] = profile
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save profile '{profile.name}': {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if profile_id not in self.profiles:
                logger.warning(f"Profile not found for deletion: {profile_id}")
                return False
            
            # Remove from memory
            profile_name = self.profiles[profile_id].name
            del self.profiles[profile_id]
            
            # Delete file
            profile_file = self.profiles_dir / f"{profile_id}.yaml"
            if profile_file.exists():
                profile_file.unlink()
            
            # Clear active profile if it was deleted
            if self.active_profile_id == profile_id:
                self.active_profile_id = None
            
            logger.info(f"Deleted profile: {profile_name} ({profile_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete profile '{profile_id}': {e}")
            return False
    
    def set_active_profile(self, profile_id: str) -> bool:
        """
        Set active profile
        
        Args:
            profile_id: Profile ID to set as active
            
        Returns:
            bool: True if set successfully
        """
        try:
            if profile_id not in self.profiles:
                logger.error(f"Cannot set active profile - profile not found: {profile_id}")
                return False
            
            self.active_profile_id = profile_id
            
            # Save to config
            if self.config_manager:
                self.config_manager.set('profile.active_profile', profile_id)
            
            logger.info(f"Active profile set to: {self.profiles[profile_id].name} ({profile_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set active profile '{profile_id}': {e}")
            return False
    
    def get_active_profile(self) -> Optional[UserProfile]:
        """Get the currently active profile"""
        if self.active_profile_id and self.active_profile_id in self.profiles:
            return self.profiles[self.active_profile_id]
        return None
    
    def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get profile by ID"""
        return self.profiles.get(profile_id)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """Get list of all profiles (without sensitive data)"""
        profile_list = []
        
        for profile_id, profile in self.profiles.items():
            profile_info = {
                'id': profile.id,
                'name': profile.name,
                'created': profile.created.isoformat() if profile.created else None,
                'modified': profile.modified.isoformat() if profile.modified else None,
                'is_active': profile.is_active,
                'tags': profile.tags,
                'notes': profile.notes[:100] + "..." if len(profile.notes) > 100 else profile.notes
            }
            
            # Add personal info summary
            profile_info['personal_summary'] = {
                'email': profile.personal.email,
                'phone': profile.personal.phone,
                'full_name': profile.personal.full_name
            }
            
            # Mark active profile
            profile_info['is_current_active'] = (profile_id == self.active_profile_id)
            
            profile_list.append(profile_info)
        
        return sorted(profile_list, key=lambda x: x['name'])
    
    def search_profiles(self, query: str) -> List[UserProfile]:
        """
        Search profiles by name, email, or tags
        
        Args:
            query: Search query
            
        Returns:
            List of matching profiles
        """
        query_lower = query.lower()
        matches = []
        
        for profile in self.profiles.values():
            # Search in name
            if query_lower in profile.name.lower():
                matches.append(profile)
                continue
            
            # Search in email
            if profile.personal.email and query_lower in profile.personal.email.lower():
                matches.append(profile)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in profile.tags):
                matches.append(profile)
                continue
            
            # Search in notes
            if profile.notes and query_lower in profile.notes.lower():
                matches.append(profile)
                continue
        
        return matches
    
    def duplicate_profile(self, source_id: str, new_name: str, new_id: str = None) -> Optional[UserProfile]:
        """
        Duplicate a profile
        
        Args:
            source_id: ID of profile to duplicate
            new_name: Name for the new profile
            new_id: Optional ID for new profile
            
        Returns:
            UserProfile: New duplicated profile
        """
        try:
            source_profile = self.get_profile(source_id)
            if not source_profile:
                logger.error(f"Source profile not found: {source_id}")
                return None
            
            # Create new ID
            if not new_id:
                new_id = self._generate_profile_id(new_name)
            
            # Duplicate profile data
            new_profile = UserProfile(
                id=new_id,
                name=new_name,
                personal=PersonalInfo(**asdict(source_profile.personal)),
                work=WorkInfo(**asdict(source_profile.work)),
                contact=ContactInfo(**asdict(source_profile.contact)),
                financial=FinancialInfo(**asdict(source_profile.financial)),
                preferences=Preferences(**asdict(source_profile.preferences)),
                tags=source_profile.tags.copy(),
                notes=f"Duplicated from {source_profile.name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # Save the new profile
            if self.save_profile(new_profile):
                self.profiles[new_id] = new_profile
                logger.info(f"Duplicated profile: {source_profile.name} -> {new_name}")
                return new_profile
            else:
                logger.error("Failed to save duplicated profile")
                return None
                
        except Exception as e:
            logger.error(f"Failed to duplicate profile '{source_id}': {e}")
            return None
    
    def get_profile_fields(self, profile_id: str = None) -> Dict[str, str]:
        """
        Get all profile fields as key-value pairs for form filling
        
        Args:
            profile_id: Profile ID (uses active if None)
            
        Returns:
            Dict of field name to value mappings
        """
        try:
            profile = self.get_profile(profile_id) if profile_id else self.get_active_profile()
            
            if not profile:
                return {}
            
            fields = {}
            
            # Personal information
            for field_name, field_value in asdict(profile.personal).items():
                if field_value:
                    fields[f"personal.{field_name}"] = str(field_value)
                    fields[field_name] = str(field_value)  # Also add without prefix
            
            # Work information
            for field_name, field_value in asdict(profile.work).items():
                if field_value:
                    fields[f"work.{field_name}"] = str(field_value)
            
            # Contact information
            for field_name, field_value in asdict(profile.contact).items():
                if field_value:
                    fields[f"contact.{field_name}"] = str(field_value)
            
            # Add auto-fill fields
            fields.update(profile.auto_fill_fields)
            
            return fields
            
        except Exception as e:
            logger.error(f"Failed to get profile fields: {e}")
            return {}
    
    def export_profile(self, profile_id: str, export_path: str, include_sensitive: bool = False) -> bool:
        """
        Export profile to JSON file
        
        Args:
            profile_id: Profile ID to export
            export_path: Path to export file
            include_sensitive: Whether to include sensitive financial data
            
        Returns:
            bool: True if exported successfully
        """
        try:
            profile = self.get_profile(profile_id)
            if not profile:
                return False
            
            # Use masked version if not including sensitive data
            export_profile = profile if include_sensitive else profile.mask_sensitive_data()
            
            export_data = export_profile.to_dict()
            export_data['exported'] = datetime.now().isoformat()
            export_data['exported_by'] = 'SafwanBuddy Profile Manager'
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported profile: {profile.name} to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export profile '{profile_id}': {e}")
            return False
    
    def import_profile(self, import_path: str, profile_id: str = None) -> Optional[UserProfile]:
        """
        Import profile from JSON file
        
        Args:
            import_path: Path to import file
            profile_id: Optional ID for imported profile
            
        Returns:
            UserProfile: Imported profile
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Remove export metadata
            if 'exported' in import_data:
                del import_data['exported']
            if 'exported_by' in import_data:
                del import_data['exported_by']
            
            # Generate ID if not provided
            if not profile_id:
                profile_id = self._generate_profile_id(import_data.get('name', 'imported'))
            
            # Create profile
            imported_profile = UserProfile(
                id=profile_id,
                name=import_data.get('name', 'Imported Profile')
            )
            
            # Load data
            if imported_profile.from_dict(import_data):
                # Save the imported profile
                if self.save_profile(imported_profile):
                    self.profiles[profile_id] = imported_profile
                    logger.info(f"Imported profile: {imported_profile.name}")
                    return imported_profile
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to import profile from {import_path}: {e}")
            return None
    
    def _generate_profile_id(self, name: str) -> str:
        """Generate a unique profile ID from name"""
        import re
        
        # Convert to lowercase and replace spaces with underscores
        base_id = re.sub(r'[^a-zA-Z0-9]', '_', name.lower()).strip('_')
        
        # Add timestamp for uniqueness
        timestamp = int(time.time())
        candidate_id = f"{base_id}_{timestamp}"
        
        # Ensure uniqueness
        original_id = candidate_id
        counter = 1
        while candidate_id in self.profiles:
            candidate_id = f"{original_id}_{counter}"
            counter += 1
        
        return candidate_id
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get profile manager statistics"""
        active_profile = self.get_active_profile()
        
        return {
            'total_profiles': len(self.profiles),
            'active_profile': active_profile.name if active_profile else None,
            'profiles_with_personal_info': sum(1 for p in self.profiles.values() if p.personal.full_name),
            'profiles_with_work_info': sum(1 for p in self.profiles.values() if p.work.company),
            'profiles_with_financial_info': sum(1 for p in self.profiles.values() if p.financial.bank_name),
            'last_modified': max((p.modified for p in self.profiles.values()), default=None)
        }

# Global profile manager instance
_profile_manager = None

def get_profile_manager(config_manager=None) -> ProfileManager:
    """Get or create global profile manager"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager(config_manager)
    return _profile_manager

def get_active_profile() -> Optional[UserProfile]:
    """Get active profile using global manager"""
    return get_profile_manager().get_active_profile()

def get_profile_fields(profile_id: str = None) -> Dict[str, str]:
    """Get profile fields using global manager"""
    return get_profile_manager().get_profile_fields(profile_id)