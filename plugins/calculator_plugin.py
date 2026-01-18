from src.safwanbuddy.core.plugin_loader import PluginBase
from src.safwanbuddy.core.logging import logger

class CalculatorPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "Calculator"
        self.description = "Performs basic math"

    def activate(self):
        self.event_bus.subscribe("voice_command", self.handle_command)

    def handle_command(self, text: str):
        if "calculate" in text.lower():
            # Very basic extraction
            try:
                expr = text.lower().replace("calculate", "").strip()
                result = eval(expr, {"__builtins__": None}, {})
                logger.info(f"Calculation Result: {result}")
                self.event_bus.emit("system_log", f"Calculator: {expr} = {result}")
            except Exception as e:
                logger.error(f"Calculation Error: {e}")

    def deactivate(self):
        self.event_bus.unsubscribe("voice_command", self.handle_command)
