from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.voice.command_processor import command_processor

class SafwanBuddyOrchestrator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SafwanBuddyOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.subsystems = {}

    def start(self):
        logger.info("Orchestrator starting subsystems...")
        # Initialization logic for all subsystems
        return True

    def process_command(self, command_text: str, voice_mode: bool = False):
        logger.info(f"Orchestrator processing command: {command_text}")
        # Pass to command processor
        command_processor.process_command(command_text)
        return f"Processed: {command_text}"

    def listen_for_command(self):
        # Trigger single-shot listen
        logger.info("Listening for single command...")
        return "mock command result"

    def stop(self):
        logger.info("Orchestrator shutting down...")
        return True

orchestrator = SafwanBuddyOrchestrator()
