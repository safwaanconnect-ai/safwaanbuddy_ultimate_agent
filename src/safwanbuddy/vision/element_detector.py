import cv2
import numpy as np
from src.safwanbuddy.vision.ocr_engine import ocr_engine

class ElementDetector:
    def __init__(self):
        pass

    def detect_elements(self, image: np.ndarray):
        # This would use computer vision to find buttons, fields, etc.
        # For now, we'll use OCR to find clickable text as a proxy for elements
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Placeholder for more advanced detection
        return ocr_engine.extract_text(image)

    def find_buttons(self, image: np.ndarray):
        """Detect rectangular button-like elements."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 50, 150)
        
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            
            if len(approx) == 4: # Rectangular
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                if 2 < aspect_ratio < 6 and w > 50 and h > 20: # Typical button shape
                    buttons.append((x, y, w, h))
        
        return buttons

    def find_input_fields(self, image: np.ndarray):
        """Detect potential input field elements."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        fields = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if aspect_ratio > 4 and w > 100 and 20 < h < 50:
                fields.append((x, y, w, h))
        
        return fields

element_detector = ElementDetector()
