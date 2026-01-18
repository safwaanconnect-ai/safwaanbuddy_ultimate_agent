from docx import Document
from src.safwanbuddy.core.logging import logger

class WordGenerator:
    def create_document(self, title: str, content: list, save_path: str):
        """
        content: list of dicts like {"type": "paragraph", "text": "..."}
        """
        doc = Document()
        doc.add_heading(title, 0)

        for item in content:
            if item["type"] == "paragraph":
                doc.add_paragraph(item["text"])
            elif item["type"] == "heading":
                doc.add_heading(item["text"], level=item.get("level", 1))

        doc.save(save_path)
        logger.info(f"Word document saved to {save_path}")

word_generator = WordGenerator()
