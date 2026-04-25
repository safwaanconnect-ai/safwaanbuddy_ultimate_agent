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
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch

            path = os.path.join(self.output_dir, filename)
            doc = SimpleDocTemplate(path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            story.append(Paragraph(title, styles['Title']))
            story.append(Spacer(1, 0.2 * inch))

            # Body
            for para in paragraphs:
                story.append(Paragraph(str(para), styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))

            doc.build(story)
            logger.info(f"PDF saved to {path}")
            return path
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            return None

pdf_generator = PDFGenerator()
