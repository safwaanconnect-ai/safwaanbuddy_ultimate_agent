import yaml
import os
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.settings: Dict[str, Any] = {}
        self.active_profile = None
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            self._create_default_config()
        
        with open(self.config_path, 'r') as f:
            self.settings = yaml.safe_load(f) or {}
            
        # Load overrides from environment variables
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
                "run_mode": "interactive"
            },
            "voice": {
                "engine": "vosk",
                "wake_word": "hey safwan",
                "language": "en"
            },
            "gui": {
                "theme": "dark",
                "opacity": 0.9,
                "holographic_ui": True
            },
            "automation": {
                "max_workers": 5,
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

    def get_config(self):
        return self.settings

    def set_config(self, key: str, value: Any):
        keys = key.split('.')
        d = self.settings
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def save_config(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self.settings, f)

    def get_profile(self, profile_id: str = None):
        # This would load from profiles.yaml
        return {"id": "default", "name": "Default Profile"}

    def set_active_profile(self, profile_id: str):
        self.active_profile = profile_id

config_manager = ConfigManager()
