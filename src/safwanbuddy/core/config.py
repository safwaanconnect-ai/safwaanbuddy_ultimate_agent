import yaml
import os
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.settings: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            self._create_default_config()
        
        with open(self.config_path, 'r') as f:
            self.settings = yaml.safe_load(f) or {}
            
        # Load overrides from environment variables if any
        # e.g., SAFWANBUDDY_API_KEY
        for key, value in os.environ.items():
            if key.startswith("SAFWANBUDDY_"):
                config_key = key.replace("SAFWANBUDDY_", "").lower()
                self.settings[config_key] = value

    def _create_default_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        default_settings = {
            "app": {
                "name": "SafwanBuddy Ultimate++",
                "version": "7.0",
                "language": "en"
            },
            "voice": {
                "engine": "vosk",
                "wake_word": "hey safwan",
                "languages": ["en", "hi", "hyderabadi"]
            },
            "gui": {
                "theme": "dark",
                "accent_color": "#00ffff"
            },
            "automation": {
                "typing_speed": "medium",
                "human_like": True
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(default_settings, f)
        self.settings = default_settings

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        val = self.settings
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

config_manager = ConfigManager()
