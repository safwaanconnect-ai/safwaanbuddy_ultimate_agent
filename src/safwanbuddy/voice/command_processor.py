from src.safwanbuddy.core import event_bus, logger
from src.safwanbuddy.voice import tts_manager, language_manager

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
        event_bus.emit("system_state", "processing")

        if not self.is_active:
            if self.wake_word in text:
                self.is_active = True
                event_bus.emit("system_state", "listening")
                tts_manager.speak("Yes, I am listening.")
                # Strip wake word
                remaining = text.split(self.wake_word)[-1].strip()
                if remaining:
                    self.execute_action(remaining)
            else:
                event_bus.emit("system_state", "idle")
        else:
            if "stop listening" in text or "goodbye" in text:
                self.is_active = False
                event_bus.emit("system_state", "idle")
                tts_manager.speak("Goodbye!")
            else:
                self.execute_action(text)
                if self.is_active:
                    event_bus.emit("system_state", "listening")

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
        elif "record workflow" in command:
            event_bus.emit("automation_request", {"action": "record_workflow"})
        elif "stop recording" in command:
            event_bus.emit("automation_request", {"action": "stop_recording"})
        elif "run workflow" in command:
            name = command.split("run workflow")[-1].strip()
            event_bus.emit("automation_request", {"action": "run_workflow", "name": name})
        elif "compare price" in command:
            product = command.split("compare price")[-1].strip()
            event_bus.emit("web_request", {"action": "compare_price", "product": product})
        elif "generate" in command and "report" in command:
            event_bus.emit("document_request", {"action": "generate_report"})
        else:
            event_bus.emit("unknown_command", command)
            event_bus.emit("system_state", "error")

command_processor = CommandProcessor()
