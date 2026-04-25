import pyautogui
import time
from src.safwanbuddy.vision import ocr_engine, screen_capture
from src.safwanbuddy.core import logger, event_bus

class ClickSystem:
    def __init__(self):
        pyautogui.FAILSAFE = True

    def _human_move(self, x, y):
        """Moves the mouse in a human-like curve."""
        pyautogui.moveTo(x, y, duration=0.5, tween=pyautogui.easeInOutQuad)

    def click_text(self, text: str, double_click: bool = False):
        logger.info(f"Attempting to click text: {text}")
        screenshot = screen_capture.capture()
        results = ocr_engine.find_text(screenshot, text)
        
        if not results:
            logger.warning(f"Could not find text '{text}' on screen.")
            return False

        # Pick the highest confidence result
        best_match = max(results, key=lambda x: x[4])
        x, y, w, h, conf = best_match
        
        center_x = x + w // 2
        center_y = y + h // 2
        
        self._human_move(center_x, center_y)
        if double_click:
            pyautogui.doubleClick()
        else:
            pyautogui.click()
            
        event_bus.emit("system_log", f"Clicked '{text}' at ({center_x}, {center_y})")
        return True

    def click_at(self, x, y, double_click=False):
        self._human_move(x, y)
        if double_click:
            pyautogui.doubleClick()
        else:
            pyautogui.click()

    def right_click_at(self, x, y):
        self._human_move(x, y)
        pyautogui.rightClick()

    def drag_and_drop(self, start_x, start_y, end_x, end_y):
        self._human_move(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=1.0)

click_system = ClickSystem()
