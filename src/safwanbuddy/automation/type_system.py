import pyautogui
import random
import time
from src.safwanbuddy.utils.helpers import human_delay
from src.safwanbuddy.core.config import config_manager
from src.safwanbuddy.profiles.profile_manager import profile_manager

class TypeSystem:
    def type_text(self, text: str, human_like: bool = True):
        if human_like:
            for char in text:
                pyautogui.write(char)
                time.sleep(random.uniform(0.05, 0.2))
        else:
            pyautogui.write(text)

    def type_profile_info(self, field: str):
        profile_id = config_manager.active_profile or "default"
        profile = profile_manager.load_profile(profile_id)
        if field in profile:
            self.type_text(str(profile[field]))
        else:
            # Fallback to general settings or some default
            pass

type_system = TypeSystem()
