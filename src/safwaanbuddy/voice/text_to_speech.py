"""Text-to-speech synthesis with language support."""

import logging
import threading
from typing import Optional

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logging.warning("pyttsx3 not available, TTS disabled")

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class TextToSpeech:
    """Text-to-speech engine wrapper."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.engine: Optional[pyttsx3.Engine] = None
        self.is_speaking = False
        self._lock = threading.Lock()
        
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize TTS engine."""
        if not PYTTSX3_AVAILABLE:
            self.logger.error("pyttsx3 not available")
            return
        
        try:
            self.engine = pyttsx3.init()
            
            rate = self.config.get("tts.rate", 150)
            volume = self.config.get("tts.volume", 0.9)
            voice_id = self.config.get("tts.voice_id")
            
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            
            self.logger.info("TTS engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
    
    def speak(self, text: str, blocking: bool = False) -> None:
        """Speak the given text.
        
        Args:
            text: Text to speak
            blocking: Wait for speech to complete
        """
        if not self.engine:
            self.logger.error("Cannot speak: engine not initialized")
            return
        
        if not text or not text.strip():
            return
        
        if blocking:
            self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()
    
    def _speak_sync(self, text: str) -> None:
        """Synchronous speak operation."""
        with self._lock:
            if self.is_speaking:
                self.engine.stop()
            
            try:
                self.is_speaking = True
                self.event_bus.emit(EventType.TTS_STARTED, {"text": text})
                
                self.logger.info(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                
                self.event_bus.emit(EventType.TTS_FINISHED, {"text": text})
            except Exception as e:
                self.logger.error(f"Error speaking: {e}")
            finally:
                self.is_speaking = False
    
    def stop(self) -> None:
        """Stop current speech."""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                self.logger.info("Speech stopped")
            except Exception as e:
                self.logger.error(f"Error stopping speech: {e}")
    
    def get_voices(self) -> list:
        """Get available voices.
        
        Returns:
            List of available voice objects
        """
        if not self.engine:
            return []
        
        try:
            return self.engine.getProperty('voices')
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> None:
        """Set voice by ID.
        
        Args:
            voice_id: Voice identifier
        """
        if not self.engine:
            self.logger.error("Cannot set voice: engine not initialized")
            return
        
        try:
            self.engine.setProperty('voice', voice_id)
            self.config.set("tts.voice_id", voice_id)
            self.logger.info(f"Voice set to: {voice_id}")
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
    
    def set_rate(self, rate: int) -> None:
        """Set speech rate.
        
        Args:
            rate: Speech rate (words per minute)
        """
        if not self.engine:
            self.logger.error("Cannot set rate: engine not initialized")
            return
        
        try:
            self.engine.setProperty('rate', rate)
            self.config.set("tts.rate", rate)
            self.logger.info(f"Speech rate set to: {rate}")
        except Exception as e:
            self.logger.error(f"Error setting rate: {e}")
    
    def set_volume(self, volume: float) -> None:
        """Set speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not self.engine:
            self.logger.error("Cannot set volume: engine not initialized")
            return
        
        volume = max(0.0, min(1.0, volume))
        
        try:
            self.engine.setProperty('volume', volume)
            self.config.set("tts.volume", volume)
            self.logger.info(f"Speech volume set to: {volume}")
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
