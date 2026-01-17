"""PDF generation using ReportLab."""

import logging
from pathlib import Path
from typing import List, Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("reportlab not available")

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class PDFGenerator:
    """Generate PDF documents."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.canvas: Optional[canvas.Canvas] = None
        self.filepath: Optional[Path] = None
    
    def create_pdf(self, filepath: Path, pagesize=letter) -> bool:
        """Create new PDF.
        
        Args:
            filepath: Output file path
            pagesize: Page size
            
        Returns:
            True if successful
        """
        if not REPORTLAB_AVAILABLE:
            self.logger.error("reportlab not available")
            return False
        
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            self.filepath = filepath
            self.canvas = canvas.Canvas(str(filepath), pagesize=pagesize)
            self.logger.info("Created new PDF")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create PDF: {e}")
            return False
    
    def add_text(self, text: str, x: float, y: float, font: str = "Helvetica", size: int = 12) -> bool:
        """Add text to PDF.
        
        Args:
            text: Text to add
            x: X position
            y: Y position
            font: Font name
            size: Font size
            
        Returns:
            True if successful
        """
        if not self.canvas:
            return False
        
        try:
            self.canvas.setFont(font, size)
            self.canvas.drawString(x, y, text)
            return True
        except Exception as e:
            self.logger.error(f"Failed to add text: {e}")
            return False
    
    def save_pdf(self) -> bool:
        """Save PDF to file.
        
        Returns:
            True if successful
        """
        if not self.canvas:
            return False
        
        try:
            self.canvas.save()
            
            self.event_bus.emit(EventType.DOCUMENT_SAVED, {
                "type": "pdf",
                "filepath": str(self.filepath)
            })
            
            self.logger.info(f"PDF saved: {self.filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save PDF: {e}")
            return False
