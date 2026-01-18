import pyautogui
import random
import time
from src.safwanbuddy.utils.helpers import human_delay

class TypeSystem:
    def type_text(self, text: str, human_like: bool = True):
        if human_like:
            for char in text:
                pyautogui.write(char)
                time.sleep(random.uniform(0.05, 0.2))
        else:
            pyautogui.write(text)

type_system = TypeSystem()
