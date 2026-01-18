from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.voice.text_to_speech import tts_manager
from src.safwanbuddy.voice.language_manager import language_manager

class CommandProcessor:
    def __init__(self):
        event_bus.subscribe("voice_command", self.process_command)
        self.wake_word = "hey safwan"
        self.is_active = False

    def process_command(self, text: str):
        text = text.lower()
        # Handle Hyderabadi translation if active
        text = language_manager.translate_hyderabadi(text)
        
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
        # Intent recognition logic
        if "open browser" in command:
            event_bus.emit("automation_request", {"action": "open_browser"})
        elif "fill form" in command:
            event_bus.emit("automation_request", {"action": "fill_form"})
        elif "search for" in command:
            query = command.split("search for")[-1].strip()
            event_bus.emit("automation_request", {"action": "search", "query": query})
        elif "type my email" in command:
            event_bus.emit("automation_request", {"action": "type_profile", "field": "email"})
        elif "call" in command:
            # Example: call Safwan
            name = command.split("call")[-1].strip()
            event_bus.emit("social_request", {"action": "call", "name": name})
        else:
            event_bus.emit("unknown_command", command)

command_processor = CommandProcessor()
