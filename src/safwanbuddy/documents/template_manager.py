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

    def add_template(self, source_path: str):
        if os.path.exists(source_path):
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.template_dir, filename)
            shutil.copy(source_path, dest_path)
            logger.info(f"Template {filename} added.")

template_manager = TemplateManager()
