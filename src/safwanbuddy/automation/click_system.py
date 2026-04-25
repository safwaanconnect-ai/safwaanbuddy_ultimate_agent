import pyautogui
from src.safwanbuddy.vision import ocr_engine, screen_capture
from src.safwanbuddy.core import logger, event_bus

class ClickSystem:
    def _human_move(self, x, y):
        """Moves the mouse in a human-like curve."""
        # Simple implementation of human-like movement
        pyautogui.moveTo(x, y, duration=0.5, tween=pyautogui.easeInOutQuad)

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
            
            self._human_move(center_x, center_y)
            
            if double_click:
                pyautogui.doubleClick()
            else:
                pyautogui.click()
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
