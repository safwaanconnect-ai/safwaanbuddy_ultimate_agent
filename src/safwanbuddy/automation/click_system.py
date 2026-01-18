import pyautogui
from src.safwanbuddy.vision.ocr_engine import ocr_engine
from src.safwanbuddy.vision.screen_capture import screen_capture
from src.safwanbuddy.core.logging import logger

class ClickSystem:
    def click_text(self, text: str, double_click: bool = False):
        screenshot = screen_capture.capture()
        results = ocr_engine.find_text(screenshot, text)
        
        if results:
            # results is expected to be a list of (x, y, w, h, confidence)
            x, y, w, h = results[0][:4]
            center_x = x + w // 2
            center_y = y + h // 2
            
            if double_click:
                pyautogui.doubleClick(center_x, center_y)
            else:
                pyautogui.click(center_x, center_y)
            return True
        else:
            logger.warning(f"Could not find text '{text}' on screen to click.")
            return False

click_system = ClickSystem()
