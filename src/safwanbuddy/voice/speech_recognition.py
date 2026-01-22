import json
import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from src.safwanbuddy.core import event_bus, logger

class VoiceRecognizer:
    def __init__(self, model_path: str = "data/models/vosk-model-small-en-us-0.15"):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_listening = False

        if not os.path.exists(self.model_path):
            # Try to find any model in the data/models directory
            models_dir = "data/models"
            if os.path.exists(models_dir):
                dirs = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
                if dirs:
                    self.model_path = os.path.join(models_dir, dirs[0])
                    logger.info(f"Using alternative Vosk model found at {self.model_path}")

        if os.path.exists(self.model_path):
            try:
                self.model = Model(self.model_path)
                self.recognizer = KaldiRecognizer(self.model, 16000)
            except Exception as e:
                logger.error(f"Failed to load Vosk model: {e}")
        else:
            logger.warning(f"Vosk model not found. Voice recognition will be disabled.")

    def callback(self, indata, frames, time, status):
        if status:
            logger.error(status)
        self.audio_queue.put(bytes(indata))

    def start_listening(self):
        if not self.model:
            return

        self.is_listening = True
        event_bus.emit("system_state", "listening")
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                   channels=1, callback=self.callback):
                while self.is_listening:
                    data = self.audio_queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            event_bus.emit("voice_command", text)
        except Exception as e:
            logger.error(f"Error in audio input stream: {e}")
            event_bus.emit("system_state", "error")
            event_bus.emit("system_log", f"Audio Error: {e}")
            self.is_listening = False

    def stop_listening(self):
        self.is_listening = False
        event_bus.emit("system_state", "idle")
