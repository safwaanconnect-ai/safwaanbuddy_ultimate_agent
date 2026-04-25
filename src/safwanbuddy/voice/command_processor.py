import re
from src.safwanbuddy.core import event_bus, logger
from src.safwanbuddy.voice import tts_manager, language_manager

class CommandProcessor:
    def __init__(self):
        event_bus.subscribe("voice_command", self.process_command)
        self.wake_word = "hey safwan"
        self.is_active = False
        
        # Define intent patterns
        self.intents = [
            (r"(?:open|launch) (?:the )?browser", "open_browser"),
            (r"(?:fill|complete) (?:the )?form", "fill_form"),
            (r"search (?:for )?(.+)", "search"),
            (r"type (?:my )?email", "type_email"),
            (r"call (.+)", "call"),
            (r"(?:send|message) (?:to )?(.+?) (?:saying|with) (.+)", "message"),
            (r"record (?:a )?workflow", "record_workflow"),
            (r"stop recording", "stop_recording"),
            (r"run workflow (.+)", "run_workflow"),
            (r"compare price (?:of )?(.+)", "compare_price"),
            (r"generate (?:a )?report", "generate_report"),
            (r"set language to (.+)", "set_language"),
        ]

    def process_command(self, text: str):
        text = text.lower().strip()
        # Handle Hyderabadi translation
        text = language_manager.translate_hyderabadi(text)
        
        logger.info(f"Processing command: {text}")
        
        if not self.is_active:
            if self.wake_word in text:
                self.is_active = True
                event_bus.emit("system_state", "listening")
                tts_manager.speak("Yes, I am listening.")
                remaining = text.split(self.wake_word)[-1].strip()
                if remaining:
                    self.execute_action(remaining)
            return

        if any(word in text for word in ["stop listening", "goodbye", "exit", "quit"]):
            self.is_active = False
            event_bus.emit("system_state", "idle")
            tts_manager.speak("Goodbye!")
            return

        self.execute_action(text)

    def execute_action(self, command: str):
        event_bus.emit("system_state", "processing")
        
        found_intent = False
        for pattern, action in self.intents:
            match = re.search(pattern, command)
            if match:
                found_intent = True
                groups = match.groups()
                self._dispatch(action, groups)
                break
        
        if not found_intent:
            logger.warning(f"Unknown command: {command}")
            event_bus.emit("unknown_command", command)
            event_bus.emit("system_state", "error")
            tts_manager.speak("I'm sorry, I didn't understand that command.")
        else:
            if self.is_active:
                event_bus.emit("system_state", "listening")

    def _dispatch(self, action, args):
        logger.info(f"Dispatching action: {action} with args: {args}")
        
        if action == "open_browser":
            event_bus.emit("automation_request", {"action": "open_browser"})
        elif action == "fill_form":
            event_bus.emit("automation_request", {"action": "fill_form"})
        elif action == "search":
            event_bus.emit("automation_request", {"action": "search", "query": args[0]})
        elif action == "type_email":
            event_bus.emit("automation_request", {"action": "type_profile", "field": "email"})
        elif action == "call":
            event_bus.emit("social_request", {"action": "call", "name": args[0]})
        elif action == "message":
            event_bus.emit("social_request", {"action": "message", "name": args[0], "message": args[1]})
        elif action == "record_workflow":
            event_bus.emit("automation_request", {"action": "record_workflow"})
        elif action == "stop_recording":
            event_bus.emit("automation_request", {"action": "stop_recording"})
        elif action == "run_workflow":
            event_bus.emit("automation_request", {"action": "run_workflow", "name": args[0]})
        elif action == "compare_price":
            event_bus.emit("web_request", {"action": "compare_price", "product": args[0]})
        elif action == "generate_report":
            event_bus.emit("document_request", {"action": "generate_report"})
        elif action == "set_language":
            lang = args[0]
            if "hindi" in lang: code = "hi"
            elif "english" in lang: code = "en"
            elif "hyderabadi" in lang: code = "hyderabadi"
            else: code = "en"
            language_manager.set_language(code)
            tts_manager.speak(f"Language set to {lang}")

command_processor = CommandProcessor()
