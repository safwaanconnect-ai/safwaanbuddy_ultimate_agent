from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.voice.text_to_speech import tts_manager

class SocialIntegrator:
    def __init__(self):
        self.platforms = {
            "WhatsApp": {"active": True},
            "Telegram": {"active": True},
            "Signal": {"active": True},
            "Messenger": {"active": True},
            "IMO": {"active": True}
        }
        self.contacts = [
            {"name": "Safwan", "phone": "12345", "platform": "WhatsApp"},
            {"name": "Manager", "phone": "67890", "platform": "Telegram"}
        ]

    def send_message(self, platform: str, contact_name: str, message: str):
        if platform in self.platforms:
            logger.info(f"Sending {platform} message to {contact_name}: {message}")
            return True
        else:
            logger.warning(f"Unsupported platform: {platform}")
            return False

    def initiate_call(self, contact_name: str, platform: str = "WhatsApp", message_to_deliver: str = None):
        logger.info(f"Initiating {platform} call to {contact_name}...")
        if message_to_deliver:
            logger.info(f"Delivering automated message: {message_to_deliver}")
            tts_manager.speak(message_to_deliver)
        return True

    def list_contacts(self):
        return [c["name"] for c in self.contacts]

    def add_contact(self, name: str, phone: str, platform: str):
        self.contacts.append({"name": name, "phone": phone, "platform": platform})
        logger.info(f"Contact {name} added.")

social_integrator = SocialIntegrator()
