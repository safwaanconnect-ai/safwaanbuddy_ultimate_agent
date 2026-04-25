from src.safwanbuddy.core import logger, event_bus
from src.safwanbuddy.voice import tts_manager
import webbrowser
import urllib.parse

class SocialIntegrator:
    def __init__(self):
        self.platforms = {
            "WhatsApp": {"active": True, "url": "https://web.whatsapp.com/send?phone={phone}&text={text}"},
            "Telegram": {"active": True, "url": "https://t.me/{username}"},
            "Messenger": {"active": True, "url": "https://m.me/{username}"}
        }
        self.contacts = [
            {"name": "Safwan", "phone": "9100000000", "platform": "WhatsApp", "username": "safwan"},
            {"name": "Manager", "phone": "9199999999", "platform": "Telegram", "username": "boss"}
        ]

    def send_message(self, contact_name: str, message: str, platform: str = None):
        contact = next((c for c in self.contacts if c["name"].lower() == contact_name.lower()), None)
        if not contact and not platform:
            logger.warning(f"Contact {contact_name} not found and no platform specified.")
            return False
            
        if not platform:
            platform = contact["platform"] if contact else "WhatsApp"
            
        if platform in self.platforms:
            logger.info(f"Preparing {platform} message to {contact_name}: {message}")
            
            encoded_msg = urllib.parse.quote(message)
            phone = contact["phone"] if contact else ""
            username = contact.get("username", "") if contact else ""
            
            url_template = self.platforms[platform]["url"]
            url = url_template.format(phone=phone, text=encoded_msg, username=username)
            
            webbrowser.open(url)
            event_bus.emit("system_log", f"Message window opened for {contact_name} on {platform}")
            tts_manager.speak(f"Opening {platform} to send message to {contact_name}")
            return True
        else:
            logger.warning(f"Unsupported platform: {platform}")
            return False

    def initiate_call(self, contact_name: str, platform: str = "WhatsApp", message_to_deliver: str = None):
        contact = next((c for c in self.contacts if c["name"].lower() == contact_name.lower()), None)
        phone = contact["phone"] if contact else contact_name
        
        logger.info(f"Initiating {platform} call to {contact_name} ({phone})...")
        # For WhatsApp, we can't easily initiate a call via URL, but we can open the chat
        if platform == "WhatsApp":
            url = f"https://web.whatsapp.com/send?phone={phone}"
            webbrowser.open(url)
            
        if message_to_deliver:
            tts_manager.speak(message_to_deliver)
        return True

    def add_contact(self, name: str, phone: str, platform: str, username: str = ""):
        self.contacts.append({"name": name, "phone": phone, "platform": platform, "username": username})
        logger.info(f"Contact {name} added.")

social_integrator = SocialIntegrator()
