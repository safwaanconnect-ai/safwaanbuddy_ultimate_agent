"""Vosk-based offline speech recognition with multi-language support."""

import json
import logging
from pathlib import Path
from typing import Optional, Callable
import sounddevice as sd
import queue
import threading

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk not available, speech recognition disabled")

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class SpeechRecognizer:
    """Offline speech recognizer using Vosk."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.model: Optional[Model] = None
        self.recognizer: Optional[KaldiRecognizer] = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.wake_word = self.config.get("voice.wake_word", "hey safwan").lower()
        self.sample_rate = 16000
        self.listening_thread: Optional[threading.Thread] = None
        
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize Vosk model."""
        if not VOSK_AVAILABLE:
            self.logger.error("Vosk not available")
            return
        
        model_dir = Path(self.config.get("voice.model_dir", "data/models/vosk"))
        
        if not model_dir.exists():
            self.logger.warning(f"Vosk model not found at {model_dir}")
            self.logger.info("Please download Vosk model from https://alphacephei.com/vosk/models")
            return
        
        try:
            self.model = Model(str(model_dir))
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.logger.info("Vosk model initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Vosk model: {e}")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def start_listening(self) -> None:
        """Start continuous listening."""
        if not self.model or not self.recognizer:
            self.logger.error("Cannot start listening: model not initialized")
            return
        
        if self.is_listening:
            self.logger.warning("Already listening")
            return
        
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()
        self.logger.info("Started listening for speech")
    
    def stop_listening(self) -> None:
        """Stop continuous listening."""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=2.0)
        self.logger.info("Stopped listening")
    
    def _listen_loop(self) -> None:
        """Main listening loop."""
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self._audio_callback
            ):
                self.logger.info("Audio stream opened")
                
                while self.is_listening:
                    try:
                        data = self.audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            self.logger.info(f"Recognized: {text}")
                            self._process_speech(text)
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get('partial', '').strip()
                        
                        if partial_text:
                            self.event_bus.emit(EventType.SPEECH_DETECTED, {"text": partial_text, "final": False})
                
        except Exception as e:
            self.logger.error(f"Error in listen loop: {e}", exc_info=True)
    
    def _process_speech(self, text: str) -> None:
        """Process recognized speech."""
        self.event_bus.emit(EventType.SPEECH_DETECTED, {"text": text, "final": True})
        
        if self.wake_word in text.lower():
            self.logger.info(f"Wake word detected: {self.wake_word}")
            self.event_bus.emit(EventType.WAKE_WORD_DETECTED, {"text": text})
            
            command = text.lower().replace(self.wake_word, '').strip()
            if command:
                self.event_bus.emit(EventType.VOICE_COMMAND, {"command": command, "text": text})
        else:
            confidence = self.config.get("voice.confidence_threshold", 0.7)
            if len(text.split()) >= 2:
                self.event_bus.emit(EventType.VOICE_COMMAND, {
                    "command": text,
                    "text": text,
                    "confidence": confidence
                })
    
    def recognize_once(self, timeout: float = 5.0) -> Optional[str]:
        """Recognize speech for a single utterance.
        
        Args:
            timeout: Maximum time to wait for speech
            
        Returns:
            Recognized text or None
        """
        if not self.model or not self.recognizer:
            self.logger.error("Cannot recognize: model not initialized")
            return None
        
        result_text = None
        
        def callback(indata, frames, time, status):
            if status:
                self.logger.warning(f"Audio callback status: {status}")
            if self.recognizer.AcceptWaveform(bytes(indata)):
                nonlocal result_text
                result = json.loads(self.recognizer.Result())
                result_text = result.get('text', '').strip()
        
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=callback
            ):
                sd.sleep(int(timeout * 1000))
            
            return result_text
        except Exception as e:
            self.logger.error(f"Error in recognize_once: {e}")
            return None
