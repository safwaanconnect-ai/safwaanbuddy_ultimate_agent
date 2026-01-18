from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.voice.text_to_speech import tts_manager

class CommandProcessor:
    def __init__(self):
        event_bus.subscribe("voice_command", self.process_command)
        self.wake_word = "hey safwan"
        self.is_active = False

    def process_command(self, text: str):
        text = text.lower()
        logger.info(f"Processing command: {text}")

        if not self.is_active:
            if self.wake_word in text:
                self.is_active = True
                tts_manager.speak("Yes, I am listening.")
                # Strip wake word
                remaining = text.split(self.wake_word)[-1].strip()
                if remaining:
                    self.execute_action(remaining)
        else:
            if "stop listening" in text or "goodbye" in text:
                self.is_active = False
                tts_manager.speak("Goodbye!")
            else:
                self.execute_action(text)

    def execute_action(self, command: str):
        # Here we would route to specific modules or plugins
        if "open browser" in command:
            event_bus.emit("automation_request", {"action": "open_browser"})
        elif "fill form" in command:
            event_bus.emit("automation_request", {"action": "fill_form"})
        else:
            event_bus.emit("unknown_command", command)
            # tts_manager.speak(f"I heard you say {command}, but I don't know how to do that yet.")

command_processor = CommandProcessor()
