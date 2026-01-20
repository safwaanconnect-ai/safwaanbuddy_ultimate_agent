from src.safwanbuddy.core.plugin_loader import PluginBase
from src.safwanbuddy.core.logging import logger

class HelloPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "Hello Plugin"
        self.description = "A simple plugin that says hello."

    def activate(self):
        logger.info(f"{self.name} activated!")
        self.event_bus.subscribe("voice_command", self.on_voice_command)

    def on_voice_command(self, text):
        if "hello" in text.lower():
            logger.info("HelloPlugin: I heard hello!")

    def deactivate(self):
        logger.info(f"{self.name} deactivated.")
