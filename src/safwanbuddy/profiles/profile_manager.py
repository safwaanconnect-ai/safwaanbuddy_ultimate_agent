import yaml
import json
import os
from src.safwanbuddy.core import logger

class ProfileManager:
    def __init__(self, data_dir: str = "data/profiles"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self._ensure_default_profiles()

    def _ensure_default_profiles(self):
        if not self.list_profiles():
            default_profile = {
                "id": "personal_1",
                "name": "Personal",
                "type": "personal",
                "full_name": "Safwan Buddy",
                "email": "safwan@example.com",
                "phone": "+1234567890",
                "address": "123 Main Street",
                "city": "Hyderabad",
                "country": "India",
                "zip_code": "500001"
            }
            self.save_profile("personal", default_profile)
            
            prof_profile = {
                "id": "professional_1",
                "name": "Professional",
                "type": "professional",
                "full_name": "Safwan Buddy",
                "email": "safwan.work@example.com",
                "company": "AI Corp",
                "title": "Senior Automation Engineer"
            }
            self.save_profile("professional", prof_profile)

    def save_profile(self, name: str, data: dict):
        file_path = os.path.join(self.data_dir, f"{name}.yaml")
        with open(file_path, 'w') as f:
            yaml.dump(data, f)
        logger.info(f"Profile {name} saved.")

    def load_profile(self, name: str) -> dict:
        file_path = os.path.join(self.data_dir, f"{name}.yaml")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def list_profiles(self):
        return [f.replace('.yaml', '') for f in os.listdir(self.data_dir) if f.endswith('.yaml')]

profile_manager = ProfileManager()
