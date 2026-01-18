from src.safwanbuddy.automation.click_system import click_system
from src.safwanbuddy.automation.type_system import type_system
from src.safwanbuddy.core.logging import logger

class FormFiller:
    def fill_form(self, profile_data: dict, field_mapping: dict):
        """
        profile_data: e.g. {"name": "Safwan", "email": "safwan@example.com"}
        field_mapping: e.g. {"Name": "name", "Email": "email"}
        """
        for label, profile_key in field_mapping.items():
            value = profile_data.get(profile_key)
            if value:
                logger.info(f"Filling field {label} with {value}")
                if click_system.click_text(label):
                    # Usually clicking the label might not focus the field, 
                    # we might need to click nearby or press Tab
                    # For simplicity, assume clicking label focuses the field
                    type_system.type_text(value)
                else:
                    logger.warning(f"Could not find field label: {label}")

form_filler = FormFiller()
