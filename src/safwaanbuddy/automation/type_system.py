"""Human-like keyboard automation with randomized delays."""

import logging
import time
import random
from typing import Optional, List
import pyautogui
import keyboard as kb

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class TypeSystem:
    """Human-like typing automation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.delay_min = self.config.get("automation.typing_delay_min", 0.05)
        self.delay_max = self.config.get("automation.typing_delay_max", 0.15)
    
    def type_text(self, text: str, human_like: bool = True, interval: Optional[float] = None) -> None:
        """Type text with optional human-like delays.
        
        Args:
            text: Text to type
            human_like: Use randomized delays
            interval: Fixed interval between keystrokes (overrides human_like)
        """
        if not text:
            return
        
        self.logger.info(f"Typing text: {text[:50]}...")
        
        try:
            if interval is not None:
                pyautogui.write(text, interval=interval)
            elif human_like:
                self._type_human_like(text)
            else:
                pyautogui.write(text)
            
            self.event_bus.emit(EventType.TYPE_PERFORMED, {"text": text})
        except Exception as e:
            self.logger.error(f"Failed to type text: {e}")
    
    def _type_human_like(self, text: str) -> None:
        """Type with human-like randomized delays."""
        for char in text:
            pyautogui.write(char)
            
            delay = random.uniform(self.delay_min, self.delay_max)
            
            if char in '.!?':
                delay *= 2
            elif char in ',;:':
                delay *= 1.5
            elif char == ' ':
                delay *= 0.8
            
            time.sleep(delay)
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.1) -> None:
        """Press a key.
        
        Args:
            key: Key name
            presses: Number of presses
            interval: Interval between presses
        """
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            self.logger.info(f"Pressed key: {key} ({presses} times)")
        except Exception as e:
            self.logger.error(f"Failed to press key: {e}")
    
    def press_hotkey(self, *keys: str) -> None:
        """Press a hotkey combination.
        
        Args:
            *keys: Keys to press together
        """
        try:
            pyautogui.hotkey(*keys)
            self.logger.info(f"Pressed hotkey: {'+'.join(keys)}")
        except Exception as e:
            self.logger.error(f"Failed to press hotkey: {e}")
    
    def hold_key(self, key: str) -> None:
        """Hold down a key.
        
        Args:
            key: Key name
        """
        try:
            pyautogui.keyDown(key)
            self.logger.info(f"Holding key: {key}")
        except Exception as e:
            self.logger.error(f"Failed to hold key: {e}")
    
    def release_key(self, key: str) -> None:
        """Release a key.
        
        Args:
            key: Key name
        """
        try:
            pyautogui.keyUp(key)
            self.logger.info(f"Released key: {key}")
        except Exception as e:
            self.logger.error(f"Failed to release key: {e}")
    
    def type_with_enter(self, text: str, human_like: bool = True) -> None:
        """Type text and press Enter.
        
        Args:
            text: Text to type
            human_like: Use human-like delays
        """
        self.type_text(text, human_like=human_like)
        time.sleep(0.2)
        self.press_key('enter')
    
    def clear_field(self, length: Optional[int] = None) -> None:
        """Clear text field.
        
        Args:
            length: Number of characters to delete (selects all if None)
        """
        try:
            if length is None:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
            else:
                for _ in range(length):
                    pyautogui.press('backspace')
                    time.sleep(0.05)
            
            pyautogui.press('delete')
            self.logger.info("Cleared field")
        except Exception as e:
            self.logger.error(f"Failed to clear field: {e}")
    
    def paste_text(self, text: str) -> None:
        """Paste text using clipboard.
        
        Args:
            text: Text to paste
        """
        try:
            pyautogui.write(text)
            self.logger.info(f"Pasted text: {text[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to paste text: {e}")
    
    def type_special(self, special_type: str) -> None:
        """Type special sequences.
        
        Args:
            special_type: Type of special sequence (email, phone, etc.)
        """
        sequences = {
            'tab': lambda: self.press_key('tab'),
            'enter': lambda: self.press_key('enter'),
            'escape': lambda: self.press_key('esc'),
            'space': lambda: self.press_key('space'),
            'backspace': lambda: self.press_key('backspace'),
            'delete': lambda: self.press_key('delete')
        }
        
        if special_type in sequences:
            sequences[special_type]()
        else:
            self.logger.warning(f"Unknown special type: {special_type}")
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if key is currently pressed.
        
        Args:
            key: Key name
            
        Returns:
            True if key is pressed
        """
        try:
            return kb.is_pressed(key)
        except Exception as e:
            self.logger.error(f"Failed to check key state: {e}")
            return False
