import pyttsx3
import threading

class TTSManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.lock = threading.Lock()

    def speak(self, text: str):
        def run():
            with self.lock:
                self.engine.say(text)
                self.engine.runAndWait()
        
        threading.Thread(target=run, daemon=True).start()

tts_manager = TTSManager()
