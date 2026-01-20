from reportlab.pdfgen import canvas
from src.safwanbuddy.core import logger

class PDFGenerator:
    def create_pdf(self, title: str, text: str, save_path: str):
        c = canvas.Canvas(save_path)
        c.drawString(100, 750, title)
        c.drawString(100, 700, text)
        c.save()
        logger.info(f"PDF document saved to {save_path}")

pdf_generator = PDFGenerator()
