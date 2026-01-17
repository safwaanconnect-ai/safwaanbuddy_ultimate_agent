"""UI element detection for buttons, links, fields, etc."""

import logging
from typing import List, Dict, Optional
from PIL import Image
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("opencv-python not available, element detection limited")

from ..core.config import ConfigManager
from .screen_capture import ScreenCapture
from .ocr_engine import OCREngine


class ElementDetector:
    """Detect UI elements on screen."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        self.screen_capture = ScreenCapture()
        self.ocr_engine = OCREngine()
    
    def detect_elements(self, element_type: str, monitor: int = 1) -> List[Dict]:
        """Detect UI elements of specific type.
        
        Args:
            element_type: Element type (button, link, field, checkbox, menu)
            monitor: Monitor number
            
        Returns:
            List of detected elements
        """
        img = self.screen_capture.capture_screen(monitor)
        
        if not img:
            return []
        
        if element_type == 'text':
            return self.ocr_engine.get_text_boxes(img)
        elif element_type == 'button':
            return self._detect_buttons(img)
        elif element_type == 'field':
            return self._detect_fields(img)
        elif element_type == 'checkbox':
            return self._detect_checkboxes(img)
        else:
            self.logger.warning(f"Unknown element type: {element_type}")
            return []
    
    def _detect_buttons(self, image: Image.Image) -> List[Dict]:
        """Detect button elements.
        
        Args:
            image: PIL Image
            
        Returns:
            List of button elements
        """
        if not CV2_AVAILABLE:
            return []
        
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                if 50 < w < 300 and 20 < h < 80:
                    aspect_ratio = w / h
                    if 1.5 < aspect_ratio < 10:
                        buttons.append({
                            'type': 'button',
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'confidence': 0.7
                        })
            
            return buttons
        except Exception as e:
            self.logger.error(f"Button detection failed: {e}")
            return []
    
    def _detect_fields(self, image: Image.Image) -> List[Dict]:
        """Detect input field elements.
        
        Args:
            image: PIL Image
            
        Returns:
            List of field elements
        """
        if not CV2_AVAILABLE:
            return []
        
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            edges = cv2.Canny(gray, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            fields = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                if 100 < w < 600 and 20 < h < 50:
                    aspect_ratio = w / h
                    if aspect_ratio > 3:
                        fields.append({
                            'type': 'field',
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'confidence': 0.6
                        })
            
            return fields
        except Exception as e:
            self.logger.error(f"Field detection failed: {e}")
            return []
    
    def _detect_checkboxes(self, image: Image.Image) -> List[Dict]:
        """Detect checkbox elements.
        
        Args:
            image: PIL Image
            
        Returns:
            List of checkbox elements
        """
        if not CV2_AVAILABLE:
            return []
        
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            checkboxes = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                if 10 < w < 30 and 10 < h < 30:
                    aspect_ratio = w / h
                    if 0.8 < aspect_ratio < 1.2:
                        checkboxes.append({
                            'type': 'checkbox',
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'confidence': 0.5
                        })
            
            return checkboxes
        except Exception as e:
            self.logger.error(f"Checkbox detection failed: {e}")
            return []
