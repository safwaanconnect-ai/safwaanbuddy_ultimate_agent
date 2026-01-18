from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.config import config_manager
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.voice.speech_recognition import VoiceRecognizer
from src.safwanbuddy.voice.command_processor import command_processor

class SafwanBuddyApp:
    def __init__(self):
        self.config = config_manager
        self.voice_recognizer = VoiceRecognizer()
        self.is_running = False

    def start(self):
        logger.info("Initializing SafwanBuddy Ultimate++ v7.0")
        self.is_running = True
        # In a real scenario, voice recognition would run in a separate thread
        # For now, we'll just log that it started
        logger.info("System Ready.")

    def stop(self):
        self.is_running = False
        logger.info("System Shutdown.")

app = SafwanBuddyApp()
