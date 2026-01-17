"""Template loading and application."""

import logging
from pathlib import Path
from typing import Dict, Optional
import yaml

from ..core.config import ConfigManager


class TemplateManager:
    """Manage document templates."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        self.templates_dir = Path("data/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def load_template(self, name: str) -> Optional[Dict]:
        """Load template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template data or None
        """
        template_file = self.templates_dir / f"{name}.yaml"
        
        if not template_file.exists():
            self.logger.error(f"Template not found: {name}")
            return None
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = yaml.safe_load(f)
            return template
        except Exception as e:
            self.logger.error(f"Failed to load template: {e}")
            return None
    
    def save_template(self, name: str, template: Dict) -> bool:
        """Save template.
        
        Args:
            name: Template name
            template: Template data
            
        Returns:
            True if successful
        """
        template_file = self.templates_dir / f"{name}.yaml"
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(template, f, default_flow_style=False)
            self.logger.info(f"Template saved: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save template: {e}")
            return False
