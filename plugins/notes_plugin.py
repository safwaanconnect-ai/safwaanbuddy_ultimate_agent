from src.safwanbuddy.core.plugin_loader import PluginBase
from src.safwanbuddy.core.logging import logger

class NotesPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "Notes Plugin"
        self.description = "Simple note taking plugin"
        self.notes = []

    def activate(self):
        logger.info("Notes Plugin Activated")

    def add_note(self, content: str):
        self.notes.append(content)
        logger.info(f"Note added: {content}")

    def get_notes(self):
        return self.notes
