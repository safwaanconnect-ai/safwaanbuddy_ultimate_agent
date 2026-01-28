#!/usr/bin/env python3
"""
Text-to-Speech Manager for SafwanBuddy
Handles voice synthesis using pyttsx3
"""

import logging
import threading
import time
from typing import Optional, Callable, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-Speech engine wrapper"""
    
    def __init__(self):
        self.engine = None
        self.voices = {}
        self.current_voice = None
        self.rate = 200
        self.volume = 0.8
        self.is_speaking = False
        self.current_text = ""
        self._lock = threading.Lock()
    
    def initialize(self) -> bool:
        """Initialize the TTS engine"""
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                for voice in voices:
                    voice_id = voice.id
                    self.voices[voice_id] = {
                        'id': voice_id,
                        'name': voice.name,
                        'gender': self._guess_gender(voice.name),
                        'language': self._guess_language(voice.name)
                    }
                
                # Set default voice
                if voices:
                    self.current_voice = voices[0].id
                    self.engine.setProperty('voice', self.current_voice)
            
            # Set default properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            logger.info(f"TTS engine initialized with {len(self.voices)} voices")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        return list(self.voices.values())
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the current voice"""
        if voice_id in self.voices:
            self.current_voice = voice_id
            if self.engine:
                self.engine.setProperty('voice', voice_id)
            logger.info(f"TTS voice set to: {self.voices[voice_id]['name']}")
            return True
        return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)"""
        self.rate = max(50, min(400, rate))  # Clamp between 50-400
        if self.engine:
            self.engine.setProperty('rate', self.rate)
        return True
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))  # Clamp between 0.0-1.0
        if self.engine:
            self.engine.setProperty('volume', self.volume)
        return True
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Speak the given text"""
        if not self.engine:
            logger.error("TTS engine not initialized")
            return False
        
        with self._lock:
            if self.is_speaking:
                logger.warning("TTS is already speaking, queueing text")
            
            self.current_text = text
            self.is_speaking = True
        
        try:
            logger.debug(f"TTS speaking: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            # Speak the text
            self.engine.say(text)
            
            if blocking:
                # Wait for speech to complete
                self.engine.runAndWait()
            else:
                # Start speaking in a separate thread
                thread = threading.Thread(target=self._speak_async)
                thread.daemon = True
                thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"TTS speaking failed: {e}")
            with self._lock:
                self.is_speaking = False
            return False
    
    def _speak_async(self):
        """Speak text asynchronously"""
        try:
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Async TTS failed: {e}")
        finally:
            with self._lock:
                self.is_speaking = False
                self.current_text = ""
    
    def stop(self):
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
                with self._lock:
                    self.is_speaking = False
                    self.current_text = ""
                logger.info("TTS stopped")
            except Exception as e:
                logger.error(f"Failed to stop TTS: {e}")
    
    def pause(self):
        """Pause current speech"""
        if self.engine:
            try:
                self.engine.pause()
                logger.info("TTS paused")
            except Exception as e:
                logger.error(f"Failed to pause TTS: {e}")
    
    def resume(self):
        """Resume paused speech"""
        if self.engine:
            try:
                self.engine.resume()
                logger.info("TTS resumed")
            except Exception as e:
                logger.error(f"Failed to resume TTS: {e}")
    
    def is_currently_speaking(self) -> bool:
        """Check if TTS is currently speaking"""
        with self._lock:
            return self.is_speaking
    
    def get_current_text(self) -> str:
        """Get currently speaking text"""
        with self._lock:
            return self.current_text
    
    def _guess_gender(self, voice_name: str) -> str:
        """Guess voice gender from name"""
        name_lower = voice_name.lower()
        if any(word in name_lower for word in ['female', 'woman', 'girl', 'zira', 'hazel', 'susan']):
            return 'female'
        elif any(word in name_lower for word in ['male', 'man', 'boy', 'david', 'mark']):
            return 'male'
        else:
            return 'unknown'
    
    def _guess_language(self, voice_name: str) -> str:
        """Guess voice language from name"""
        name_lower = voice_name.lower()
        if any(word in name_lower for word in ['english', 'us', 'uk', 'australia']):
            return 'en'
        elif any(word in name_lower for word in ['spanish', 'español']):
            return 'es'
        elif any(word in name_lower for word in ['french', 'français']):
            return 'fr'
        elif any(word in name_lower for word in ['german', 'deutsch']):
            return 'de'
        elif any(word in name_lower for word in ['italian', 'italiano']):
            return 'it'
        elif any(word in name_lower for word in ['portuguese', 'português']):
            return 'pt'
        elif any(word in name_lower for word in ['russian', 'русский']):
            return 'ru'
        elif any(word in name_lower for word in ['chinese', '中文']):
            return 'zh'
        elif any(word in name_lower for word in ['japanese', '日本語']):
            return 'ja'
        elif any(word in name_lower for word in ['korean', '한국어']):
            return 'ko'
        else:
            return 'unknown'

class TTSManager:
    """Complete TTS management system"""
    
    def __init__(self, config_manager=None):
        """
        Initialize TTS Manager
        
        Args:
            config_manager: Configuration manager for settings
        """
        self.config_manager = config_manager
        self.engine = TTSEngine()
        self.is_initialized = False
        self.listeners = {}
        
        # Configuration defaults
        self.default_rate = 200
        self.default_volume = 0.8
        self.default_voice = None
        
        # Load configuration if available
        self._load_config()
        
        # Initialize engine
        self._initialize()
    
    def _load_config(self):
        """Load TTS configuration"""
        if not self.config_manager:
            return
        
        try:
            # Load voice settings from config
            rate = self.config_manager.get('voice.speech_rate', 200)
            volume = self.config_manager.get('voice.speech_volume', 0.8)
            voice_id = self.config_manager.get('voice.voice_id', 'default')
            
            self.default_rate = rate
            self.default_volume = volume
            self.default_voice = voice_id
            
            logger.debug(f"TTS config loaded: rate={rate}, volume={volume}, voice={voice_id}")
            
        except Exception as e:
            logger.warning(f"Failed to load TTS config: {e}")
    
    def _initialize(self) -> bool:
        """Initialize the TTS system"""
        try:
            if self.engine.initialize():
                # Apply configuration
                self.engine.set_rate(self.default_rate)
                self.engine.set_volume(self.default_volume)
                
                if self.default_voice and self.default_voice != 'default':
                    self.engine.set_voice(self.default_voice)
                
                self.is_initialized = True
                logger.info("TTS Manager initialized successfully")
                return True
            else:
                logger.error("Failed to initialize TTS engine")
                return False
                
        except Exception as e:
            logger.error(f"TTS initialization error: {e}")
            return False
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """
        Speak text
        
        Args:
            text: Text to speak
            blocking: Whether to wait for speech to complete
            
        Returns:
            bool: True if speech started successfully
        """
        if not self.is_initialized:
            logger.error("TTS not initialized")
            return False
        
        # Clean and prepare text
        text = self._clean_text(text)
        
        if not text.strip():
            logger.warning("Empty text provided to TTS")
            return False
        
        try:
            # Emit pre-speech event
            self._emit_event('pre_speech', {'text': text})
            
            # Speak the text
            success = self.engine.speak(text, blocking)
            
            if success:
                logger.info(f"TTS: {text[:100]}{'...' if len(text) > 100 else ''}")
                
                # Start monitoring thread for speech completion
                if not blocking:
                    thread = threading.Thread(target=self._monitor_speech, args=(text,))
                    thread.daemon = True
                    thread.start()
            else:
                self._emit_event('speech_error', {'text': text, 'error': 'Speech failed to start'})
            
            return success
            
        except Exception as e:
            logger.error(f"TTS speaking error: {e}")
            self._emit_event('speech_error', {'text': text, 'error': str(e)})
            return False
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for speech"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Replace common abbreviations for better pronunciation
        replacements = {
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Dr.': 'Doctor',
            'Prof.': 'Professor',
            'St.': 'Street',
            'etc.': 'etcetera',
            'i.e.': 'that is',
            'e.g.': 'for example'
        }
        
        for abbrev, full in replacements.items():
            text = text.replace(abbrev, full)
        
        # Handle numbers
        text = self._handle_numbers(text)
        
        return text
    
    def _handle_numbers(self, text: str) -> str:
        """Convert numbers to spoken form"""
        import re
        
        # Simple number conversion (can be enhanced)
        def replace_number(match):
            num = match.group()
            try:
                # Handle simple cases
                if num.isdigit():
                    return self._number_to_words(int(num))
                else:
                    return num
            except:
                return num
        
        # Replace standalone numbers
        text = re.sub(r'\b\d+\b', replace_number, text)
        
        return text
    
    def _number_to_words(self, num: int) -> str:
        """Convert number to words (basic implementation)"""
        if num == 0:
            return "zero"
        elif num < 0:
            return f"negative {self._number_to_words(abs(num))}"
        elif num < 20:
            words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", 
                    "seventeen", "eighteen", "nineteen"]
            return words[num - 1]
        elif num < 100:
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            if num < 20:
                return self._number_to_words(num)
            else:
                return tens[num // 10] + ("" if num % 10 == 0 else " " + self._number_to_words(num % 10))
        elif num < 1000:
            hundreds = self._number_to_words(num // 100) + " hundred"
            remainder = num % 100
            return hundreds + ("" if remainder == 0 else " " + self._number_to_words(remainder))
        else:
            return str(num)  # Fallback for larger numbers
    
    def _monitor_speech(self, text: str):
        """Monitor speech completion and emit events"""
        while self.engine.is_currently_speaking():
            time.sleep(0.1)
        
        # Emit completion event
        self._emit_event('speech_completed', {'text': text})
    
    def stop(self):
        """Stop current speech"""
        if self.engine:
            self.engine.stop()
            logger.info("TTS stopped by user")
    
    def pause(self):
        """Pause current speech"""
        if self.engine:
            self.engine.pause()
    
    def resume(self):
        """Resume paused speech"""
        if self.engine:
            self.engine.resume()
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate"""
        if self.engine.set_rate(rate):
            # Save to config
            if self.config_manager:
                self.config_manager.set('voice.speech_rate', rate)
            return True
        return False
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume"""
        if self.engine.set_volume(volume):
            # Save to config
            if self.config_manager:
                self.config_manager.set('voice.speech_volume', volume)
            return True
        return False
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the voice"""
        if self.engine.set_voice(voice_id):
            # Save to config
            if self.config_manager:
                self.config_manager.set('voice.voice_id', voice_id)
            return True
        return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available voices"""
        return self.engine.get_available_voices()
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current TTS settings"""
        return {
            'rate': self.engine.rate,
            'volume': self.engine.volume,
            'voice': self.engine.current_voice,
            'is_speaking': self.engine.is_currently_speaking(),
            'current_text': self.engine.get_current_text()
        }
    
    def add_listener(self, event_name: str, callback: Callable):
        """Add event listener"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
    
    def remove_listener(self, event_name: str, callback: Callable):
        """Remove event listener"""
        if event_name in self.listeners:
            try:
                self.listeners[event_name].remove(callback)
            except ValueError:
                pass
    
    def _emit_event(self, event_name: str, data: Dict[str, Any]):
        """Emit event to listeners"""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in TTS event listener: {e}")
    
    def test_voice(self, test_text: str = None) -> bool:
        """Test the voice with sample text"""
        if not test_text:
            test_text = "Hello! This is SafwanBuddy testing the text to speech system."
        
        return self.speak(test_text, blocking=True)
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about current voice"""
        if not self.engine.current_voice:
            return {}
        
        voice_info = self.engine.voices.get(self.engine.current_voice, {})
        return {
            **voice_info,
            'rate': self.engine.rate,
            'volume': self.engine.volume,
            'is_speaking': self.engine.is_currently_speaking()
        }
    
    def speak_list(self, text_list: List[str], pause_between: float = 0.5) -> bool:
        """Speak a list of text items with pauses"""
        if not text_list:
            return False
        
        try:
            for i, text in enumerate(text_list):
                if i > 0:
                    time.sleep(pause_between)
                
                if not self.speak(text):
                    logger.warning(f"Failed to speak item {i+1}/{len(text_list)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in speak_list: {e}")
            return False
    
    def speak_with_pronunciation(self, text: str, pronunciation_map: Dict[str, str]) -> str:
        """
        Speak text with custom pronunciations
        
        Args:
            text: Text to speak
            pronunciation_map: Dictionary mapping words to pronunciations
            
        Returns:
            Processed text
        """
        processed_text = text
        for word, pronunciation in pronunciation_map.items():
            processed_text = processed_text.replace(word, pronunciation)
        
        self.speak(processed_text)
        return processed_text

# Convenience functions
_tts_manager = None

def get_tts_manager(config_manager=None) -> TTSManager:
    """Get or create global TTS manager"""
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager(config_manager)
    return _tts_manager

def speak(text: str, blocking: bool = False) -> bool:
    """Speak text using global TTS manager"""
    return get_tts_manager().speak(text, blocking)

def set_tts_rate(rate: int) -> bool:
    """Set TTS rate"""
    return get_tts_manager().set_rate(rate)

def set_tts_volume(volume: float) -> bool:
    """Set TTS volume"""
    return get_tts_manager().set_volume(volume)

def set_tts_voice(voice_id: str) -> bool:
    """Set TTS voice"""
    return get_tts_manager().set_voice(voice_id)

def stop_tts():
    """Stop TTS"""
    get_tts_manager().stop()