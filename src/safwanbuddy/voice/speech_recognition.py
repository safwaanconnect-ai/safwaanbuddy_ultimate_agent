import json
import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from src.safwanbuddy.core import event_bus, logger

class VoiceRecognizer:
    def __init__(self, model_path: str = "assets/models/vosk-model-small-en-us-0.15"):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_listening = False

        if os.path.exists(model_path):
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
        else:
            logger.warning(f"Vosk model not found at {model_path}. Voice recognition will be disabled.")

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
