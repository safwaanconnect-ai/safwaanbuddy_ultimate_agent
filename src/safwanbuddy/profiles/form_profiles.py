from typing import Dict, Any

class FormProfile:
    def __init__(self, name: str, data: Dict[str, Any]):
        self.name = name
        self.data = data

    def get_field(self, field_name: str) -> Any:
        return self.data.get(field_name)

# Default field mappings for common forms
DEFAULT_FIELD_MAPPINGS = {
    "first_name": ["first name", "fname", "given name"],
    "last_name": ["last name", "lname", "surname", "family name"],
    "email": ["email", "e-mail", "email address"],
    "phone": ["phone", "mobile", "tel", "contact number"],
    "address": ["address", "street", "location"],
    "city": ["city", "town"],
    "zip": ["zip", "postal code", "postcode"]
}
