"""Configuration management with YAML support."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration with YAML and environment overrides."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._config: Dict[str, Any] = {}
        self._config_dir = Path(__file__).parent.parent.parent.parent / "config"
        self._env_loaded = False
        self._initialized = True
        
        self._load_env()
        self._load_default_config()
    
    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        if not self._env_loaded:
            env_file = Path(__file__).parent.parent.parent.parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
            self._env_loaded = True
    
    def _load_default_config(self) -> None:
        """Load default configuration."""
        self._config = {
            "app": {
                "name": "SafwaanBuddy Ultimate++",
                "version": "7.0.0",
                "debug": os.getenv("DEBUG", "false").lower() == "true"
            },
            "voice": {
                "enabled": True,
                "wake_word": "hey safwan",
                "languages": ["en-US", "hi-IN", "en-IN"],
                "default_language": "en-US",
                "model_dir": "data/models/vosk",
                "confidence_threshold": 0.7
            },
            "tts": {
                "enabled": True,
                "rate": 150,
                "volume": 0.9,
                "voice_id": None
            },
            "gui": {
                "theme": "dark",
                "width": 1200,
                "height": 800,
                "opacity": 0.95,
                "overlay_color": "#00ffff",
                "animation_speed": 1.0
            },
            "automation": {
                "typing_delay_min": 0.05,
                "typing_delay_max": 0.15,
                "click_delay": 0.5,
                "ocr_confidence": 0.6,
                "screenshot_quality": 85
            },
            "browser": {
                "default": "chrome",
                "headless": False,
                "window_size": [1920, 1080],
                "timeout": 30
            },
            "search": {
                "default_engine": "google",
                "max_results": 10
            },
            "profiles": {
                "data_dir": "data/profiles",
                "default_profile": "personal"
            },
            "plugins": {
                "dir": "src/safwaanbuddy/plugins",
                "enabled": []
            },
            "security": {
                "encryption_enabled": True,
                "key_file": "data/.key"
            },
            "logging": {
                "level": "INFO",
                "dir": "logs",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
    
    def load_config(self, config_file: Optional[Path] = None) -> None:
        """Load configuration from YAML file.
        
        Args:
            config_file: Path to config file
        """
        if config_file is None:
            config_file = self._config_dir / "config.yaml"
        
        config_file = Path(config_file)
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    self._deep_update(self._config, loaded_config)
    
    def save_config(self, config_file: Optional[Path] = None) -> None:
        """Save configuration to YAML file.
        
        Args:
            config_file: Path to config file
        """
        if config_file is None:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            config_file = self._config_dir / "config.yaml"
        
        config_file = Path(config_file)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'voice.enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        env_key = '_'.join(keys).upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._parse_env_value(env_value)
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'voice.enabled')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _deep_update(self, base: Dict, update: Dict) -> None:
        """Deep update dictionary."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value."""
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        try:
            return int(value)
        except ValueError:
            pass
        
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config
