import os
import shutil
from src.safwanbuddy.core import logger

class TemplateManager:
    def __init__(self, template_dir: str = "data/templates"):
        self.template_dir = template_dir
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)

    def list_templates(self):
        return os.listdir(self.template_dir)

    def get_template_path(self, template_name: str):
        path = os.path.join(self.template_dir, template_name)
        if os.path.exists(path):
            return path
        return None

    def fill_template(self, template_name: str, data: dict, output_path: str):
        """Fills a template with data. Currently supports simple string replacement in text-based files."""
        template_path = self.get_template_path(template_name)
        if not template_path:
            logger.error(f"Template {template_name} not found.")
            return False
            
        try:
            if template_name.endswith(('.txt', '.html', '.md')):
                with open(template_path, 'r') as f:
                    content = f.read()
                
                for key, value in data.items():
                    placeholder = f"{{{{{key}}}}}"
                    content = content.replace(placeholder, str(value))
                
                with open(output_path, 'w') as f:
                    f.write(content)
                logger.info(f"Template {template_name} filled and saved to {output_path}")
                return True
            else:
                logger.warning("Template filling currently only supported for text-based files.")
                return False
        except Exception as e:
            logger.error(f"Error filling template {template_name}: {e}")
            return False

template_manager = TemplateManager()
