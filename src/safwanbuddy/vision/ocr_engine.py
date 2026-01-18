import pytesseract
import cv2
import numpy as np

class OCREngine:
    def __init__(self, tesseract_cmd: str = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image: np.ndarray) -> str:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(gray)

    def find_text(self, image: np.ndarray, target_text: str):
        # Using image_to_data for positional information
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        matches = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if target_text.lower() in data['text'][i].lower():
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                matches.append((x, y, w, h, data['conf'][i]))
        
        return matches

ocr_engine = OCREngine()
