"""Tesseract-based OCR engine."""

import logging
from typing import List, Dict, Optional
from PIL import Image
import numpy as np

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available, OCR disabled")

from ..core.config import ConfigManager
from .screen_capture import ScreenCapture


class OCREngine:
    """OCR engine for text recognition."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        self.screen_capture = ScreenCapture()
    
    def extract_text(self, image: Image.Image, lang: str = 'eng') -> str:
        """Extract text from image.
        
        Args:
            image: PIL Image
            lang: Language code
            
        Returns:
            Extracted text
        """
        if not TESSERACT_AVAILABLE:
            self.logger.error("Tesseract not available")
            return ""
        
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def extract_text_from_screen(self, monitor: int = 1, lang: str = 'eng') -> str:
        """Extract text from screen.
        
        Args:
            monitor: Monitor number
            lang: Language code
            
        Returns:
            Extracted text
        """
        img = self.screen_capture.capture_screen(monitor)
        
        if img:
            return self.extract_text(img, lang)
        
        return ""
    
    def find_text(self, search_text: str, confidence: float = 0.6, monitor: int = 1) -> List[Dict]:
        """Find text on screen.
        
        Args:
            search_text: Text to find
            confidence: Minimum confidence threshold
            monitor: Monitor number
            
        Returns:
            List of found text locations
        """
        if not TESSERACT_AVAILABLE:
            self.logger.error("Tesseract not available")
            return []
        
        img = self.screen_capture.capture_screen(monitor)
        
        if not img:
            return []
        
        try:
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            results = []
            search_lower = search_text.lower()
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])
                
                if text and conf >= confidence * 100:
                    if search_lower in text.lower():
                        results.append({
                            'text': text,
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i],
                            'confidence': conf / 100.0
                        })
            
            return results
        except Exception as e:
            self.logger.error(f"Text search failed: {e}")
            return []
    
    def get_text_boxes(self, image: Image.Image, confidence: float = 0.6) -> List[Dict]:
        """Get all text boxes from image.
        
        Args:
            image: PIL Image
            confidence: Minimum confidence threshold
            
        Returns:
            List of text boxes
        """
        if not TESSERACT_AVAILABLE:
            self.logger.error("Tesseract not available")
            return []
        
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            boxes = []
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])
                
                if text and conf >= confidence * 100:
                    boxes.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': conf / 100.0
                    })
            
            return boxes
        except Exception as e:
            self.logger.error(f"Text box detection failed: {e}")
            return []
