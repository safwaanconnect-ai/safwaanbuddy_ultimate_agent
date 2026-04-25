from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from src.safwanbuddy.core import logger
import os

class PDFGenerator:
    def __init__(self):
        self.output_dir = "output/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)

    def create_pdf(self, title: str, paragraphs: list, filename: str = "document.pdf"):
        try:
            path = os.path.join(self.output_dir, filename)
            c = canvas.Canvas(path, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2.0, height - 50, title)
            
            c.setFont("Helvetica", 12)
            y = height - 100
            for para in paragraphs:
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 50
                
                # Simple text wrapping could be added here
                c.drawString(50, y, para)
                y -= 20
                
            c.save()
            logger.info(f"PDF saved to {path}")
            return path
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            return None

pdf_generator = PDFGenerator()
