import yaml
import json
import os
from src.safwanbuddy.core.logging import logger

class ProfileManager:
    def __init__(self, data_dir: str = "data/profiles"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

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
