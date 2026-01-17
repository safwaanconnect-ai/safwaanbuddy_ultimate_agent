"""Notes plugin for quick text note taking."""

from pathlib import Path
from datetime import datetime
from typing import List

from ..plugins.plugin_loader import PluginBase


class NotesPlugin(PluginBase):
    """Simple note-taking plugin."""
    
    @property
    def name(self):
        return "Notes"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self):
        self.notes_dir = Path("data/notes")
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("Notes plugin initialized")
        return True
    
    def execute(self, action: str, *args, **kwargs):
        """Execute notes action.
        
        Args:
            action: Action to perform (create, list, read, delete)
            
        Returns:
            Action result
        """
        if action == "create":
            return self._create_note(kwargs.get("content", ""))
        elif action == "list":
            return self._list_notes()
        elif action == "read":
            return self._read_note(kwargs.get("filename", ""))
        elif action == "delete":
            return self._delete_note(kwargs.get("filename", ""))
        else:
            return f"Unknown action: {action}"
    
    def _create_note(self, content: str) -> str:
        """Create new note."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"note_{timestamp}.txt"
        filepath = self.notes_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Created note: {filename}")
            return f"Note created: {filename}"
        except Exception as e:
            self.logger.error(f"Failed to create note: {e}")
            return f"Error: {e}"
    
    def _list_notes(self) -> List[str]:
        """List all notes."""
        notes = [f.name for f in self.notes_dir.glob("*.txt")]
        return sorted(notes, reverse=True)
    
    def _read_note(self, filename: str) -> str:
        """Read note content."""
        filepath = self.notes_dir / filename
        
        if not filepath.exists():
            return f"Note not found: {filename}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading note: {e}"
    
    def _delete_note(self, filename: str) -> str:
        """Delete note."""
        filepath = self.notes_dir / filename
        
        if not filepath.exists():
            return f"Note not found: {filename}"
        
        try:
            filepath.unlink()
            self.logger.info(f"Deleted note: {filename}")
            return f"Note deleted: {filename}"
        except Exception as e:
            return f"Error deleting note: {e}"
