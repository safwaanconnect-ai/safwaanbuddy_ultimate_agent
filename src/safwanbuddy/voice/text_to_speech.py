import pyttsx3
import threading

class TTSManager:
    def __init__(self):
        self.engine = None
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            from src.safwanbuddy.core.logging import logger
            logger.error(f"Failed to initialize TTS engine: {e}")
        self.lock = threading.Lock()

    def speak(self, text: str):
        if not self.engine:
            return
        def run():
            with self.lock:
                self.engine.say(text)
                self.engine.runAndWait()
        
        threading.Thread(target=run, daemon=True).start()

tts_manager = TTSManager()
