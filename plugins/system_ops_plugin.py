from src.safwanbuddy.core.plugin_loader import PluginBase
from src.safwanbuddy.core.logging import logger
import os

class SystemOpsPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "System Operations"
        self.description = "Handles system commands"

    def activate(self):
        self.event_bus.subscribe("voice_command", self.handle_command)

    def handle_command(self, text: str):
        text = text.lower()
        if "lock workstation" in text:
            logger.info("Locking workstation...")
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif "open notepad" in text:
            os.system("notepad.exe")

    def deactivate(self):
        self.event_bus.unsubscribe("voice_command", self.handle_command)
