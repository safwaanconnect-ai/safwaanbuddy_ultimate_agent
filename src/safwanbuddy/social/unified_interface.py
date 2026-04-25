from src.safwanbuddy.core import logger
from src.safwanbuddy.voice import tts_manager

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

    def send_message(self, contact_name: str, message: str, platform: str = None):
        contact = next((c for c in self.contacts if c["name"].lower() == contact_name.lower()), None)
        if not platform:
            platform = contact["platform"] if contact else "WhatsApp"
            
        if platform in self.platforms:
            logger.info(f"Sending {platform} message to {contact_name}: {message}")
            # Mock implementation of sending message
            # Real implementation would call API or use selenium/web automation
            from src.safwanbuddy.core import event_bus
            event_bus.emit("system_log", f"Message sent to {contact_name} via {platform}")
            return True
        else:
            logger.warning(f"Unsupported platform: {platform}")
            return False

    def broadcast_message(self, contact_list: list, message: str, platform: str = "WhatsApp"):
        """Sends a message to multiple contacts."""
        results = []
        for contact in contact_list:
            res = self.send_message(contact, message, platform)
            results.append(res)
        return all(results)

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
