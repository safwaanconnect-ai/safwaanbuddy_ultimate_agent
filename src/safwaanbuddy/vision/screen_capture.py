"""Fast screen capture with multi-monitor support using mss."""

import logging
from typing import Optional, Tuple, List
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logging.warning("mss not available, screen capture disabled")

from ..core.config import ConfigManager


class ScreenCapture:
    """Fast screen capture system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        self.sct: Optional[mss.mss] = None
        
        if MSS_AVAILABLE:
            self.sct = mss.mss()
    
    def capture_screen(self, monitor: int = 1) -> Optional[Image.Image]:
        """Capture entire screen.
        
        Args:
            monitor: Monitor number (1=primary, 0=all monitors)
            
        Returns:
            PIL Image or None
        """
        if not self.sct:
            self.logger.error("Screen capture not available")
            return None
        
        try:
            screenshot = self.sct.grab(self.sct.monitors[monitor])
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            return img
        except Exception as e:
            self.logger.error(f"Failed to capture screen: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """Capture screen region.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Region width
            height: Region height
            
        Returns:
            PIL Image or None
        """
        if not self.sct:
            self.logger.error("Screen capture not available")
            return None
        
        try:
            monitor = {"top": y, "left": x, "width": width, "height": height}
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            return img
        except Exception as e:
            self.logger.error(f"Failed to capture region: {e}")
            return None
    
    def capture_to_numpy(self, monitor: int = 1) -> Optional[np.ndarray]:
        """Capture screen as numpy array.
        
        Args:
            monitor: Monitor number
            
        Returns:
            Numpy array or None
        """
        img = self.capture_screen(monitor)
        if img:
            return np.array(img)
        return None
    
    def save_screenshot(self, filepath: Path, monitor: int = 1) -> bool:
        """Save screenshot to file.
        
        Args:
            filepath: Output file path
            monitor: Monitor number
            
        Returns:
            True if successful
        """
        img = self.capture_screen(monitor)
        
        if img:
            try:
                filepath = Path(filepath)
                filepath.parent.mkdir(parents=True, exist_ok=True)
                
                quality = self.config.get("automation.screenshot_quality", 85)
                img.save(filepath, quality=quality, optimize=True)
                
                self.logger.info(f"Screenshot saved: {filepath}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to save screenshot: {e}")
                return False
        
        return False
    
    def get_monitors(self) -> List[dict]:
        """Get list of available monitors.
        
        Returns:
            List of monitor info dictionaries
        """
        if not self.sct:
            return []
        
        return self.sct.monitors
    
    def get_screen_size(self, monitor: int = 1) -> Tuple[int, int]:
        """Get screen size.
        
        Args:
            monitor: Monitor number
            
        Returns:
            (width, height) tuple
        """
        if not self.sct:
            return (1920, 1080)
        
        mon = self.sct.monitors[monitor]
        return (mon['width'], mon['height'])
