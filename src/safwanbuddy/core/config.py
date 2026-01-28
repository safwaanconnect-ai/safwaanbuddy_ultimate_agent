#!/usr/bin/env python3
"""
Configuration Management for SafwanBuddy
Handles loading, saving, and managing application configuration
"""

import yaml
import os
import logging
import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class VoiceSettings:
    """Voice recognition and synthesis settings"""
    engine: str = "google"  # google, sphinx, pocketsphinx
    language: str = "en-US"
    wake_word: str = "hey safwan"
    speech_rate: float = 200.0
    speech_volume: float = 0.8
    voice_id: str = "default"
    auto_listen: bool = True
    noise_reduction: bool = True
    energy_threshold: float = 300.0
    pause_threshold: float = 0.8

@dataclass
class GUISettings:
    """GUI and visual settings"""
    theme: str = "dark"  # dark, light, holographic
    opacity: float = 0.95
    window_width: int = 1200
    window_height: int = 800
    always_on_top: bool = False
    minimize_to_tray: bool = True
    show_waveform: bool = True
    show_system_stats: bool = True
    animation_speed: float = 1.0
    holographic_effects: bool = True

@dataclass
class AutomationSettings:
    """Desktop automation settings"""
    max_workers: int = 5
    human_like_delays: bool = True
    click_delay_range: tuple = (0.1, 0.5)
    type_delay_range: tuple = (0.05, 0.15)
    screenshot_quality: int = 90
    ocr_language: str = "eng"
    timeout_seconds: int = 30
    retry_attempts: int = 3

@dataclass
class LoggingSettings:
    """Logging configuration"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    file_enabled: bool = True
    file_path: str = "logs/safwanbuddy.log"
    console_enabled: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class AppSettings:
    """Application settings"""
    name: str = "SafwanBuddy Ultimate++"
    version: str = "7.0"
    debug: bool = False
    run_mode: str = "gui"  # gui, headless, demo
    data_dir: str = "data"
    config_dir: str = "config"
    auto_start: bool = False
    profile_on_startup: str = "default"
    check_updates: bool = True

@dataclass
class APISettings:
    """API and service integration settings"""
    openai_api_key: str = ""
    google_api_key: str = ""
    weather_api_key: str = ""
    news_api_key: str = ""
    custom_apis: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_apis is None:
            self.custom_apis = {}

@dataclass
class Config:
    """Complete configuration structure"""
    app: AppSettings = None
    voice: VoiceSettings = None
    gui: GUISettings = None
    automation: AutomationSettings = None
    logging: LoggingSettings = None
    api: APISettings = None
    custom: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.app is None:
            self.app = AppSettings()
        if self.voice is None:
            self.voice = VoiceSettings()
        if self.gui is None:
            self.gui = GUISettings()
        if self.automation is None:
            self.automation = AutomationSettings()
        if self.logging is None:
            self.logging = LoggingSettings()
        if self.api is None:
            self.api = APISettings()
        if self.custom is None:
            self.custom = {}

class ConfigManager:
    """Manager for application configuration"""
    
    def __init__(self, config_dir: str = None, environment: str = "production"):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory for configuration files
            environment: Environment (development, testing, production)
        """
        # Set up paths
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path(__file__).parent.parent.parent / "config"
        
        self.environment = environment
        self.config_file = self.config_dir / "config.yaml"
        self.secrets_file = self.config_dir / "secrets.yaml"
        self.backup_dir = self.config_dir / "backups"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.config: Config = None
        self._config_lock = threading.Lock() if 'threading' in globals() else None
        
        # Load configuration
        self.load_config()
    
    def load_config(self, reset: bool = False) -> Config:
        """
        Load configuration from file
        
        Args:
            reset: If True, create fresh default configuration
            
        Returns:
            Config: Loaded configuration object
        """
        if reset:
            self.config = Config()
            self.save_config()
            return self.config
        
        # Check if config file exists
        if not self.config_file.exists():
            logger.info("Configuration file not found, creating default configuration")
            self.config = Config()
            self._create_default_config()
            return self.config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Create config object from loaded data
            self.config = self._dict_to_config(data)
            
            # Load secrets if available
            self._load_secrets()
            
            # Apply environment overrides
            self._apply_environment_overrides()
            
            logger.info(f"Configuration loaded from {self.config_file}")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            self.config = Config()
            return self.config
    
    def save_config(self, backup: bool = True) -> bool:
        """
        Save configuration to file
        
        Args:
            backup: If True, create backup before saving
            
        Returns:
            bool: True if saved successfully
        """
        if not self.config:
            logger.error("No configuration to save")
            return False
        
        try:
            # Create backup if requested
            if backup and self.config_file.exists():
                self._create_backup()
            
            # Convert config to dict
            config_dict = self._config_to_dict(self.config)
            
            # Add metadata
            config_dict['_metadata'] = {
                'version': self.config.app.version,
                'last_modified': datetime.now().isoformat(),
                'environment': self.environment
            }
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2, allow_unicode=True)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'voice.language')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self.config:
            return default
        
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'voice.language')
            value: Value to set
            
        Returns:
            bool: True if set successfully
        """
        if not self.config:
            return False
        
        keys = key.split('.')
        obj = self.config
        
        try:
            # Navigate to the parent object
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
            elif isinstance(obj, dict):
                obj[final_key] = value
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set configuration key '{key}': {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self.config = Config()
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate current configuration
        
        Returns:
            Dict with validation results: {'valid': bool, 'errors': [...], 'warnings': [...]}
        """
        errors = []
        warnings = []
        
        if not self.config:
            errors.append("No configuration loaded")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate voice settings
        if self.config.voice.speech_rate < 50 or self.config.voice.speech_rate > 400:
            warnings.append("Voice speech rate should be between 50-400")
        
        if self.config.voice.energy_threshold < 100:
            warnings.append("Voice energy threshold seems very low")
        
        # Validate GUI settings
        if self.config.gui.opacity < 0.1 or self.config.gui.opacity > 1.0:
            errors.append("GUI opacity must be between 0.1 and 1.0")
        
        if self.config.gui.window_width < 800 or self.config.gui.window_height < 600:
            warnings.append("GUI window size may be too small for optimal experience")
        
        # Validate automation settings
        if self.config.automation.timeout_seconds < 5:
            warnings.append("Automation timeout seems very short")
        
        if self.config.automation.retry_attempts < 1:
            warnings.append("Automation retry attempts should be at least 1")
        
        # Check for required directories
        if not Path(self.config.app.data_dir).exists():
            warnings.append(f"Data directory does not exist: {self.config.app.data_dir}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> Config:
        """Convert dictionary to Config object"""
        try:
            # Handle metadata
            if '_metadata' in data:
                data.pop('_metadata')
            
            # Create config sections
            app_data = data.get('app', {})
            voice_data = data.get('voice', {})
            gui_data = data.get('gui', {})
            automation_data = data.get('automation', {})
            logging_data = data.get('logging', {})
            api_data = data.get('api', {})
            custom_data = data.get('custom', {})
            
            # Create config objects
            config = Config(
                app=AppSettings(**app_data),
                voice=VoiceSettings(**voice_data),
                gui=GUISettings(**gui_data),
                automation=AutomationSettings(**automation_data),
                logging=LoggingSettings(**logging_data),
                api=APISettings(**api_data),
                custom=custom_data
            )
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to convert dict to config: {e}")
            return Config()
    
    def _config_to_dict(self, config: Config) -> Dict[str, Any]:
        """Convert Config object to dictionary"""
        return {
            'app': asdict(config.app),
            'voice': asdict(config.voice),
            'gui': asdict(config.gui),
            'automation': asdict(config.automation),
            'logging': asdict(config.logging),
            'api': asdict(config.api),
            'custom': config.custom
        }
    
    def _create_default_config(self):
        """Create default configuration file"""
        try:
            # Create default config
            self.config = Config()
            
            # Add some default custom settings
            self.config.custom = {
                'startup_commands': [],
                'custom_intents': {},
                'ui_layout': 'default',
                'shortcuts': {
                    'toggle_mic': 'Ctrl+Shift+M',
                    'show_help': 'F1',
                    'quick_command': 'Ctrl+Shift+Q'
                }
            }
            
            # Save the configuration
            self.save_config()
            
            # Create example secrets file
            self._create_secrets_template()
            
            logger.info("Default configuration created")
            
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    def _create_secrets_template(self):
        """Create template for secrets configuration"""
        secrets_template = {
            '#api_keys': {
                'openai_api_key': 'your_openai_api_key_here',
                'google_api_key': 'your_google_api_key_here',
                'weather_api_key': 'your_weather_api_key_here',
                'news_api_key': 'your_news_api_key_here',
                'custom_apis': {
                    'service_name': 'api_key_here'
                }
            },
            '#security_notes': [
                'Keep this file secure and never commit it to version control',
                'Use environment variables for production deployments',
                'Never share your API keys with others'
            ]
        }
        
        try:
            with open(self.secrets_file, 'w', encoding='utf-8') as f:
                yaml.dump(secrets_template, f, default_flow_style=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to create secrets template: {e}")
    
    def _load_secrets(self):
        """Load API keys and secrets from separate file"""
        if not self.secrets_file.exists():
            logger.debug("Secrets file not found, skipping secret loading")
            return
        
        try:
            with open(self.secrets_file, 'r', encoding='utf-8') as f:
                secrets = yaml.safe_load(f) or {}
            
            # Load API keys
            api_keys = secrets.get('#api_keys', {})
            if api_keys:
                for key, value in api_keys.items():
                    if key == 'custom_apis' and isinstance(value, dict):
                        # Merge custom APIs
                        for service, api_key in value.items():
                            self.config.api.custom_apis[service] = api_key
                    else:
                        # Set API key
                        if hasattr(self.config.api, key):
                            setattr(self.config.api, key, value)
            
            logger.debug("Secrets loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        for key, value in os.environ.items():
            if key.startswith('SAFWANBUDDY_'):
                config_key = key.replace('SAFWANBUDDY_', '').lower()
                
                # Try to set the configuration value
                if self.set(config_key, value):
                    logger.debug(f"Applied environment override: {config_key}")
    
    def _create_backup(self):
        """Create backup of current configuration"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.yaml"
            
            import shutil
            shutil.copy2(self.config_file, backup_file)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            logger.debug(f"Created configuration backup: {backup_file}")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backup files"""
        try:
            backup_files = list(self.backup_dir.glob("config_backup_*.yaml"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def export_config(self, export_path: str, include_secrets: bool = False) -> bool:
        """
        Export configuration to file
        
        Args:
            export_path: Path to export file
            include_secrets: If True, include API keys and secrets
            
        Returns:
            bool: True if exported successfully
        """
        try:
            export_data = self._config_to_dict(self.config)
            
            if include_secrets and self.secrets_file.exists():
                with open(self.secrets_file, 'r', encoding='utf-8') as f:
                    secrets = yaml.safe_load(f) or {}
                export_data['secrets'] = secrets.get('#api_keys', {})
            
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, indent=2, allow_unicode=True)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str, merge: bool = True) -> bool:
        """
        Import configuration from file
        
        Args:
            import_path: Path to import file
            merge: If True, merge with existing config; if False, replace
            
        Returns:
            bool: True if imported successfully
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = yaml.safe_load(f) or {}
            
            # Remove metadata if present
            if '_metadata' in import_data:
                import_data.pop('_metadata')
            
            if merge and self.config:
                # Merge with existing configuration
                current_dict = self._config_to_dict(self.config)
                merged_dict = self._deep_merge(current_dict, import_data)
                self.config = self._dict_to_config(merged_dict)
            else:
                # Replace configuration
                self.config = self._dict_to_config(import_data)
            
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        if not self.config:
            return {'loaded': False}
        
        return {
            'loaded': True,
            'version': self.config.app.version,
            'environment': self.environment,
            'voice_engine': self.config.voice.engine,
            'gui_theme': self.config.gui.theme,
            'data_dir': self.config.app.data_dir,
            'last_modified': self.config_file.stat().st_mtime if self.config_file.exists() else None
        }

# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get or create global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# Convenience functions
def get_config() -> Config:
    """Get current configuration"""
    return get_config_manager().config

def set_config_value(key: str, value: Any) -> bool:
    """Set configuration value"""
    return get_config_manager().set(key, value)

def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return get_config_manager().get(key, default)