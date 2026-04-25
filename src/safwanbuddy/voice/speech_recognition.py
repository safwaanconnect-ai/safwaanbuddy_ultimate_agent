import json
import os
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
from src.safwanbuddy.core import event_bus, logger

class VoiceRecognizer:
    def __init__(self, models_config: dict = None):
        if models_config is None:
            models_config = {
                "en": "assets/models/vosk-model-small-en-us-0.15",
                "hi": "assets/models/vosk-model-small-hi-0.22"
            }
        
        self.models = {}
        self.recognizers = {}
        self.current_lang = "en"
        self.audio_queue = queue.Queue()
        self.is_listening = False

        for lang, path in models_config.items():
            if os.path.exists(path):
                logger.info(f"Loading Vosk model for {lang} from {path}")
                model = Model(path)
                self.models[lang] = model
                self.recognizers[lang] = KaldiRecognizer(model, 16000)
            else:
                logger.warning(f"Vosk model for {lang} not found at {path}.")

        if not self.models:
            logger.error("No Vosk models loaded. Voice recognition will be disabled.")

    def set_language(self, lang):
        if lang in self.recognizers:
            self.current_lang = lang
            logger.info(f"Voice recognition language set to {lang}")
            return True
        return False

    def callback(self, indata, frames, time, status):
        if status:
            logger.error(status)
        self.audio_queue.put(bytes(indata))

    def start_listening(self):
        if not self.recognizers:
            return

        self.is_listening = True
        event_bus.emit("system_state", "listening")
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                   channels=1, callback=self.callback):
                while self.is_listening:
                    data = self.audio_queue.get()
                    recognizer = self.recognizers.get(self.current_lang)
                    if recognizer and recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            event_bus.emit("voice_command", text)
                    
                    # Also emit audio level for visualizer
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    level = np.abs(audio_data).mean() / 32768.0
                    event_bus.emit("audio_level", float(level))
                    
        except Exception as e:
            logger.error(f"Error in audio input stream: {e}")
            event_bus.emit("system_state", "error")
            event_bus.emit("system_log", f"Audio Error: {e}")
            self.is_listening = False


    def stop_listening(self):
        self.is_listening = False
        event_bus.emit("system_state", "idle")
