import pyttsx3
import threading

class TTSManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.lock = threading.Lock()
        self._setup_voice()

    def _setup_voice(self):
        voices = self.engine.getProperty('voices')
        # Try to find a nice voice, default to index 0
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 175)  # Speed percent
        self.engine.setProperty('volume', 0.9)  # Volume 0-1

    def set_voice(self, index: int):
        voices = self.engine.getProperty('voices')
        if 0 <= index < len(voices):
            self.engine.setProperty('voice', voices[index].id)
            return True
        return False

    def speak(self, text: str):
        if not text:
            return
        def run():
            with self.lock:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"TTS Error: {e}")
        
        threading.Thread(target=run, daemon=True).start()

tts_manager = TTSManager()
