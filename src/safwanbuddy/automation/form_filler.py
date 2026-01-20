from src.safwanbuddy.automation.click_system import click_system
from src.safwanbuddy.automation.type_system import type_system
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.vision.screen_capture import screen_capture
from src.safwanbuddy.vision.ocr_engine import ocr_engine
import time

class FormFiller:
    def __init__(self):
        self.is_filling = False
        self.pending_fields = []
        self.current_field = None
        self.results = []
        event_bus.subscribe("target_selected", self._on_field_confirmed)

    def fill_form(self, profile_data: dict, field_mapping: dict):
        """
        Standard automated fill.
        """
        for label, profile_key in field_mapping.items():
            value = profile_data.get(profile_key)
            if value:
                logger.info(f"Filling field {label} with {value}")
                if click_system.click_text(label):
                    type_system.type_text(value)
                else:
                    logger.warning(f"Could not find field label: {label}")

    def start_guided_fill(self, profile_data: dict):
        """
        Starts the interactive guided form-filling workflow.
        """
        logger.info("Starting guided form fill...")
        self.is_filling = True
        self.results = []
        
        # Capture screen and find potential fields
        screenshot = screen_capture.capture()
        # Mock detection: find all text on screen as potential labels
        data = ocr_engine.find_text(screenshot, "") # Empty string matches everything with confidence
        
        # Filter for common form field labels
        common_labels = ["name", "email", "phone", "address", "city", "country", "zip", "password", "user"]
        self.pending_fields = []
        
        for x, y, w, h, conf in data:
            # Simple heuristic: if text matches a common label
            # We'll just use a few for demonstration
            # In a real app, this would be much more sophisticated
            pass

        # For demo purposes, let's assume we found some matches based on profile keys
        for key, value in profile_data.items():
            matches = ocr_engine.find_text(screenshot, key.replace("_", " "))
            if matches:
                self.pending_fields.append({"label": key, "value": value, "rect": matches[0][:4]})

        if not self.pending_fields:
            logger.warning("No fields detected for guided fill.")
            event_bus.emit("notification", "No fields detected.")
            return

        event_bus.emit("system_log", f"Detected {len(self.pending_fields)} fields.")
        self._present_next_field()

    def _present_next_field(self):
        if not self.pending_fields:
            self._finish_guided_fill()
            return

        self.current_field = self.pending_fields.pop(0)
        label = self.current_field["label"]
        rect = self.current_field["rect"]
        
        event_bus.emit("notification", f"Fill {label}? [Space] Confirm, [Tab] Skip")
        event_bus.emit("show_targets", [rect]) # Highlight the field

    def _on_field_confirmed(self, target):
        if not self.is_filling or not self.current_field:
            return

        # User pressed Space
        label = self.current_field["label"]
        value = self.current_field["value"]
        x, y, w, h = self.current_field["rect"]
        
        import pyautogui
        pyautogui.click(x + w + 20, y + h // 2) # Click slightly to the right of label
        time.sleep(0.2)
        type_system.type_text(value)
        
        self.results.append(f"Filled {label}")
        self._present_next_field()

    def _finish_guided_fill(self):
        self.is_filling = False
        summary = ", ".join(self.results) if self.results else "No fields filled."
        event_bus.emit("system_log", f"Guided fill complete: {summary}")
        event_bus.emit("notification", "Guided fill complete.")

form_filler = FormFiller()
