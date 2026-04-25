import pytesseract
import cv2
import numpy as np

class OCREngine:
    def __init__(self, tesseract_cmd: str = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing for better OCR results."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def extract_text(self, image: np.ndarray) -> str:
        processed = self._preprocess(image)
        return pytesseract.image_to_string(processed)

    def find_text(self, image: np.ndarray, target_text: str):
        processed = self._preprocess(image)
        # Using image_to_data for positional information
        data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
        
        matches = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if target_text.lower() in data['text'][i].lower():
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                matches.append((x, y, w, h, data['conf'][i]))
        
        return matches

ocr_engine = OCREngine()
