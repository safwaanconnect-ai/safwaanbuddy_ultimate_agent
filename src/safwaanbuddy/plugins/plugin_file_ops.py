"""File operations plugin."""

import os
import shutil
from pathlib import Path
from typing import List

from ..plugins.plugin_loader import PluginBase


class FileOpsPlugin(PluginBase):
    """File operations plugin."""
    
    @property
    def name(self):
        return "File Operations"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self):
        self.logger.info("File operations plugin initialized")
        return True
    
    def execute(self, action: str, *args, **kwargs):
        """Execute file operation.
        
        Args:
            action: Action to perform (list, copy, move, delete, create_dir)
            
        Returns:
            Operation result
        """
        if action == "list":
            return self._list_files(kwargs.get("path", "."))
        elif action == "copy":
            return self._copy_file(kwargs.get("src"), kwargs.get("dst"))
        elif action == "move":
            return self._move_file(kwargs.get("src"), kwargs.get("dst"))
        elif action == "delete":
            return self._delete_file(kwargs.get("path"))
        elif action == "create_dir":
            return self._create_directory(kwargs.get("path"))
        else:
            return f"Unknown action: {action}"
    
    def _list_files(self, path: str) -> List[str]:
        """List files in directory."""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return []
            
            files = [f.name for f in path_obj.iterdir()]
            return sorted(files)
        except Exception as e:
            self.logger.error(f"List files error: {e}")
            return []
    
    def _copy_file(self, src: str, dst: str) -> str:
        """Copy file."""
        if not src or not dst:
            return "Error: Source and destination required"
        
        try:
            shutil.copy2(src, dst)
            self.logger.info(f"Copied {src} to {dst}")
            return f"File copied: {src} -> {dst}"
        except Exception as e:
            return f"Copy error: {e}"
    
    def _move_file(self, src: str, dst: str) -> str:
        """Move file."""
        if not src or not dst:
            return "Error: Source and destination required"
        
        try:
            shutil.move(src, dst)
            self.logger.info(f"Moved {src} to {dst}")
            return f"File moved: {src} -> {dst}"
        except Exception as e:
            return f"Move error: {e}"
    
    def _delete_file(self, path: str) -> str:
        """Delete file."""
        if not path:
            return "Error: Path required"
        
        try:
            path_obj = Path(path)
            if path_obj.is_file():
                path_obj.unlink()
            elif path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                return f"Path not found: {path}"
            
            self.logger.info(f"Deleted: {path}")
            return f"Deleted: {path}"
        except Exception as e:
            return f"Delete error: {e}"
    
    def _create_directory(self, path: str) -> str:
        """Create directory."""
        if not path:
            return "Error: Path required"
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {path}")
            return f"Directory created: {path}"
        except Exception as e:
            return f"Create directory error: {e}"
