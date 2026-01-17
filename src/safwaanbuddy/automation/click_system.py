"""OCR-based smart clicking with multi-target selection."""

import logging
import time
from typing import Optional, List, Tuple
import pyautogui

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager
from ..vision.ocr_engine import OCREngine
from ..vision.element_detector import ElementDetector


class ClickSystem:
    """Smart clicking system with OCR-based element detection."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.ocr_engine = OCREngine()
        self.element_detector = ElementDetector()
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.config.get("automation.click_delay", 0.5)
    
    def click_text(self, text: str, confidence: float = 0.6, click_offset: Tuple[int, int] = (0, 0)) -> bool:
        """Click on text found via OCR.
        
        Args:
            text: Text to find and click
            confidence: Minimum OCR confidence
            click_offset: Offset from text center (x, y)
            
        Returns:
            True if successful
        """
        self.logger.info(f"Searching for text: {text}")
        
        locations = self.ocr_engine.find_text(text, confidence=confidence)
        
        if not locations:
            self.logger.warning(f"Text not found: {text}")
            return False
        
        location = locations[0]
        x = location['x'] + location['width'] // 2 + click_offset[0]
        y = location['y'] + location['height'] // 2 + click_offset[1]
        
        return self.click_at(x, y)
    
    def click_at(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.1) -> bool:
        """Click at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Interval between clicks
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Clicking at ({x}, {y})")
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            
            self.event_bus.emit(EventType.CLICK_PERFORMED, {
                "x": x,
                "y": y,
                "button": button,
                "clicks": clicks
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to click: {e}")
            return False
    
    def click_element(self, element_type: str, text: Optional[str] = None, index: int = 0) -> bool:
        """Click on detected UI element.
        
        Args:
            element_type: Type of element (button, link, field, etc.)
            text: Text content to match (optional)
            index: Element index if multiple found
            
        Returns:
            True if successful
        """
        self.logger.info(f"Searching for {element_type} element")
        
        elements = self.element_detector.detect_elements(element_type)
        
        if text:
            elements = [el for el in elements if text.lower() in el.get('text', '').lower()]
        
        if not elements:
            self.logger.warning(f"Element not found: {element_type}")
            return False
        
        if index >= len(elements):
            self.logger.warning(f"Element index out of range: {index}/{len(elements)}")
            return False
        
        element = elements[index]
        x = element['x'] + element['width'] // 2
        y = element['y'] + element['height'] // 2
        
        return self.click_at(x, y)
    
    def double_click_at(self, x: int, y: int) -> bool:
        """Double click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful
        """
        return self.click_at(x, y, clicks=2, interval=0.1)
    
    def right_click_at(self, x: int, y: int) -> bool:
        """Right click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful
        """
        return self.click_at(x, y, button='right')
    
    def click_relative(self, x_offset: int, y_offset: int, from_current: bool = True) -> bool:
        """Click relative to current position or screen.
        
        Args:
            x_offset: X offset
            y_offset: Y offset
            from_current: Relative to current mouse position
            
        Returns:
            True if successful
        """
        if from_current:
            current_x, current_y = pyautogui.position()
            x = current_x + x_offset
            y = current_y + y_offset
        else:
            screen_width, screen_height = pyautogui.size()
            x = x_offset if x_offset >= 0 else screen_width + x_offset
            y = y_offset if y_offset >= 0 else screen_height + y_offset
        
        return self.click_at(x, y)
    
    def move_to(self, x: int, y: int, duration: float = 0.5) -> None:
        """Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            self.logger.info(f"Moved to ({x}, {y})")
        except Exception as e:
            self.logger.error(f"Failed to move mouse: {e}")
    
    def drag_to(self, x: int, y: int, duration: float = 0.5, button: str = 'left') -> bool:
        """Drag mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Drag duration in seconds
            button: Mouse button to hold
            
        Returns:
            True if successful
        """
        try:
            pyautogui.dragTo(x, y, duration=duration, button=button)
            self.logger.info(f"Dragged to ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to drag: {e}")
            return False
    
    def scroll(self, amount: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll at position.
        
        Args:
            amount: Scroll amount (positive=up, negative=down)
            x: X coordinate (current position if None)
            y: Y coordinate (current position if None)
        """
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
            
            pyautogui.scroll(amount)
            self.logger.info(f"Scrolled {amount} units")
        except Exception as e:
            self.logger.error(f"Failed to scroll: {e}")
