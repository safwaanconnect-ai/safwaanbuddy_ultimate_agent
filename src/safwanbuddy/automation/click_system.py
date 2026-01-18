import pyautogui
from src.safwanbuddy.vision.ocr_engine import ocr_engine
from src.safwanbuddy.vision.screen_capture import screen_capture
from src.safwanbuddy.core.logging import logger

class ClickSystem:
    def click_text(self, text: str, double_click: bool = False):
        screenshot = screen_capture.capture()
        results = ocr_engine.find_text(screenshot, text)
        
        if not results:
            logger.warning(f"Could not find text '{text}' on screen to click.")
            return False

        if len(results) == 1:
            x, y, w, h = results[0][:4]
            center_x = x + w // 2
            center_y = y + h // 2
            
            if double_click:
                pyautogui.doubleClick(center_x, center_y)
            else:
                pyautogui.click(center_x, center_y)
            from src.safwanbuddy.core.events import event_bus
            event_bus.emit("system_log", f"Clicked: {text}")
            return True
        else:
            logger.info(f"Multiple matches found for '{text}'. Showing selection overlay.")
            from src.safwanbuddy.core.events import event_bus
            # Simplify results to just (x, y, w, h)
            targets = [r[:4] for r in results]
            event_bus.emit("show_targets", targets)
            return True

click_system = ClickSystem()
