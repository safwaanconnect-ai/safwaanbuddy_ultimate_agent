#!/usr/bin/env python3
"""
Voice Recognition Manager for SafwanBuddy
Handles real-time speech recognition using speech_recognition library
"""

import logging
import threading
import time
import queue
import numpy as np
from typing import Optional, Callable, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class VoiceCommand:
    """Voice command data structure"""
    text: str
    confidence: float
    timestamp: float
    duration: float
    raw_audio: bytes = None
    source: str = "microphone"

@dataclass
class VoiceSettings:
    """Voice recognition settings"""
    language: str = "en-US"
    energy_threshold: float = 300.0
    dynamic_energy_threshold: bool = True
    pause_threshold: float = 0.8
    phrase_timeout: float = 0.5
    timeout: float = None
    phrase_time_limit: float = 10.0
    mic_index: int = None
    sample_rate: int = 16000

class AudioProcessor:
    """Processes audio data for visualization and analysis"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.audio_buffer = []
        self.max_buffer_size = 30  # 30 seconds of audio buffer
    
    def process_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process audio data and return analysis
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Dict with analysis results
        """
        try:
            # Convert bytes to numpy array for processing
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate audio metrics
            volume = np.sqrt(np.mean(audio_array**2))
            max_volume = np.max(np.abs(audio_array))
            
            # Calculate frequency spectrum (simplified)
            fft = np.fft.fft(audio_array)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio_array), 1/self.sample_rate)
            
            # Get dominant frequency
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]
            dominant_freq_idx = np.argmax(positive_magnitude)
            dominant_frequency = positive_freqs[dominant_freq_idx]
            
            # Normalize volume for visualization (0-1 range)
            normalized_volume = min(1.0, volume / 32768.0)
            
            # Store in buffer for real-time visualization
            self._add_to_buffer(normalized_volume)
            
            return {
                'volume': float(volume),
                'max_volume': float(max_volume),
                'normalized_volume': float(normalized_volume),
                'dominant_frequency': float(dominant_frequency),
                'audio_length': len(audio_array) / self.sample_rate,
                'waveform_data': self._generate_waveform(audio_array)
            }
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return {
                'volume': 0.0,
                'max_volume': 0.0,
                'normalized_volume': 0.0,
                'dominant_frequency': 0.0,
                'audio_length': 0.0,
                'waveform_data': []
            }
    
    def _add_to_buffer(self, volume: float):
        """Add volume data to buffer"""
        self.audio_buffer.append(volume)
        
        # Keep buffer size manageable
        if len(self.audio_buffer) > self.max_buffer_size:
            self.audio_buffer.pop(0)
    
    def _generate_waveform(self, audio_array: np.ndarray) -> List[float]:
        """Generate waveform data for visualization"""
        try:
            # Downsample for visualization
            if len(audio_array) > 1000:
                step = len(audio_array) // 1000
                audio_array = audio_array[::step]
            
            # Normalize to 0-1 range
            max_val = np.max(np.abs(audio_array))
            if max_val > 0:
                waveform = np.abs(audio_array) / max_val
            else:
                waveform = np.zeros_like(audio_array)
            
            return waveform.tolist()
            
        except Exception as e:
            logger.error(f"Waveform generation error: {e}")
            return []
    
    def get_recent_volume_data(self, count: int = 50) -> List[float]:
        """Get recent volume data for visualization"""
        return self.audio_buffer[-count:] if self.audio_buffer else []
    
    def clear_buffer(self):
        """Clear audio buffer"""
        self.audio_buffer.clear()

class VoiceRecognizer:
    """Real-time voice recognition with microphone input"""
    
    def __init__(self, settings: VoiceSettings = None):
        """
        Initialize voice recognizer
        
        Args:
            settings: Voice recognition settings
        """
        self.settings = settings or VoiceSettings()
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.is_paused = False
        self.listening_thread = None
        self.command_queue = queue.Queue()
        self.audio_processor = AudioProcessor(self.settings.sample_rate)
        self.listeners = {}
        
        # Recognition state
        self.last_command_time = 0
        self.command_timeout = 3.0  # Minimum time between commands
        self.ambient_noise_adjusted = False
        
        # Statistics
        self.stats = {
            'commands_recognized': 0,
            'recognition_errors': 0,
            'microphone_errors': 0,
            'listening_duration': 0.0
        }
    
    def initialize(self) -> bool:
        """Initialize voice recognition components"""
        try:
            import speech_recognition as sr
            
            # Initialize recognizer
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer settings
            self.recognizer.energy_threshold = self.settings.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.settings.dynamic_energy_threshold
            self.recognizer.pause_threshold = self.settings.pause_threshold
            
            # Initialize microphone
            if self.settings.mic_index is not None:
                self.microphone = sr.Microphone(device_index=self.settings.mic_index)
            else:
                self.microphone = sr.Microphone()
            
            # Test microphone
            if self._test_microphone():
                logger.info("Voice recognizer initialized successfully")
                return True
            else:
                logger.error("Microphone test failed")
                return False
                
        except Exception as e:
            logger.error(f"Voice recognizer initialization failed: {e}")
            return False
    
    def _test_microphone(self) -> bool:
        """Test microphone functionality"""
        try:
            with self.microphone as source:
                logger.info("Testing microphone...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.ambient_noise_adjusted = True
                logger.info("Microphone test successful")
                return True
                
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            self.stats['microphone_errors'] += 1
            return False
    
    def start_listening(self) -> bool:
        """Start continuous listening"""
        if self.is_listening:
            logger.warning("Already listening")
            return False
        
        try:
            self.is_listening = True
            self.is_paused = False
            
            # Start listening thread
            self.listening_thread = threading.Thread(target=self._listening_loop, daemon=True)
            self.listening_thread.start()
            
            logger.info("Started voice recognition listening")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        self.is_paused = False
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2.0)
        
        logger.info("Stopped voice recognition listening")
    
    def pause_listening(self):
        """Pause listening (keep thread alive but don't process)"""
        self.is_paused = True
        logger.info("Voice recognition paused")
    
    def resume_listening(self):
        """Resume listening after pause"""
        self.is_paused = False
        logger.info("Voice recognition resumed")
    
    def _listening_loop(self):
        """Main listening loop"""
        logger.debug("Voice recognition loop started")
        
        while self.is_listening:
            try:
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                # Listen for audio with timeout
                with self.microphone as source:
                    # Adjust for ambient noise if not done yet
                    if not self.ambient_noise_adjusted:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                        self.ambient_noise_adjusted = True
                    
                    try:
                        # Listen for audio
                        audio = self.recognizer.listen(
                            source, 
                            timeout=1.0, 
                            phrase_time_limit=self.settings.phrase_time_limit
                        )
                        
                        # Process the audio in a separate thread
                        thread = threading.Thread(
                            target=self._process_audio,
                            args=(audio,),
                            daemon=True
                        )
                        thread.start()
                        
                    except Exception as e:
                        logger.debug(f"Listening timeout or error: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Voice recognition loop error: {e}")
                time.sleep(1.0)
        
        logger.debug("Voice recognition loop stopped")
    
    def _process_audio(self, audio):
        """Process recognized audio"""
        start_time = time.time()
        
        try:
            # Process audio for visualization
            audio_analysis = self.audio_processor.process_audio(audio.get_raw_data())
            self._emit_event('audio_data', audio_analysis)
            
            # Skip if too soon after last command
            current_time = time.time()
            if current_time - self.last_command_time < self.command_timeout:
                return
            
            # Try to recognize speech
            text = None
            confidence = 0.0
            
            # Try Google Speech Recognition (most accurate)
            try:
                text = self.recognizer.recognize_google(audio, language=self.settings.language)
                confidence = 0.9  # Google doesn't provide confidence scores
                
            except sr.UnknownValueError:
                # Google couldn't understand audio
                logger.debug("Google Speech Recognition could not understand audio")
                self.stats['recognition_errors'] += 1
                return
                
            except sr.RequestError as e:
                # Google service error
                logger.warning(f"Google Speech Recognition error: {e}")
                self.stats['recognition_errors'] += 1
                
                # Try Sphinx as fallback (offline)
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    confidence = 0.7
                    logger.info("Used Sphinx fallback recognition")
                    
                except Exception as fallback_error:
                    logger.debug(f"Sphinx fallback failed: {fallback_error}")
                    self.stats['recognition_errors'] += 1
                    return
            
            if text and text.strip():
                # Create voice command
                duration = time.time() - start_time
                command = VoiceCommand(
                    text=text.strip(),
                    confidence=confidence,
                    timestamp=current_time,
                    duration=duration,
                    raw_audio=audio.get_raw_data()
                )
                
                # Update statistics
                self.last_command_time = current_time
                self.stats['commands_recognized'] += 1
                self.stats['listening_duration'] += duration
                
                # Add to command queue
                try:
                    self.command_queue.put_nowait(command)
                    self._emit_event('command_recognized', {
                        'command': text,
                        'confidence': confidence,
                        'duration': duration
                    })
                    logger.info(f"Voice command recognized: '{text}' (confidence: {confidence:.2f})")
                    
                except queue.Full:
                    logger.warning("Command queue full, dropping command")
                    
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            self.stats['recognition_errors'] += 1
    
    def get_next_command(self, timeout: float = None) -> Optional[VoiceCommand]:
        """Get next recognized command from queue"""
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def recognize_once(self, timeout: float = None, phrase_time_limit: float = None) -> Optional[VoiceCommand]:
        """
        Recognize speech once (blocking call)
        
        Args:
            timeout: Timeout for listening
            phrase_time_limit: Maximum time for phrase
            
        Returns:
            VoiceCommand or None
        """
        if not self.microphone or not self.recognizer:
            logger.error("Voice recognizer not initialized")
            return None
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                if not self.ambient_noise_adjusted:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self.ambient_noise_adjusted = True
                
                logger.info("Listening for speech...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout or self.settings.timeout,
                    phrase_time_limit=phrase_time_limit or self.settings.phrase_time_limit
                )
                
                # Process immediately
                start_time = time.time()
                
                # Try recognition
                text = None
                confidence = 0.0
                
                try:
                    text = self.recognizer.recognize_google(audio, language=self.settings.language)
                    confidence = 0.9
                    
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return None
                    
                except sr.RequestError as e:
                    logger.error(f"Recognition service error: {e}")
                    return None
                
                if text:
                    duration = time.time() - start_time
                    return VoiceCommand(
                        text=text.strip(),
                        confidence=confidence,
                        timestamp=start_time,
                        duration=duration,
                        raw_audio=audio.get_raw_data()
                    )
                    
        except Exception as e:
            logger.error(f"Single recognition error: {e}")
            return None
        
        return None
    
    def get_audio_analysis(self) -> Dict[str, Any]:
        """Get current audio analysis for visualization"""
        recent_volume = self.audio_processor.get_recent_volume_data()
        
        return {
            'recent_volume': recent_volume,
            'is_listening': self.is_listening,
            'is_paused': self.is_paused,
            'stats': self.stats.copy()
        }
    
    def calibrate_microphone(self, duration: float = 5.0) -> bool:
        """
        Calibrate microphone for ambient noise
        
        Args:
            duration: Calibration duration in seconds
            
        Returns:
            bool: True if calibration successful
        """
        try:
            with self.microphone as source:
                logger.info(f"Calibrating microphone for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.ambient_noise_adjusted = True
                
                # Update settings with new energy threshold
                self.settings.energy_threshold = self.recognizer.energy_threshold
                
                logger.info(f"Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
                return True
                
        except Exception as e:
            logger.error(f"Microphone calibration failed: {e}")
            return False
    
    def set_energy_threshold(self, threshold: float):
        """Set energy threshold for voice detection"""
        self.recognizer.energy_threshold = threshold
        self.settings.energy_threshold = threshold
        logger.info(f"Energy threshold set to {threshold}")
    
    def get_microphone_list(self) -> List[Dict[str, Any]]:
        """Get list of available microphones"""
        try:
            import speech_recognition as sr
            microphones = []
            
            for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
                try:
                    # Test microphone
                    mic = sr.Microphone(device_index=i)
                    with mic as source:
                        pass  # Just test that we can create it
                    
                    microphones.append({
                        'index': i,
                        'name': mic_name,
                        'available': True
                    })
                    
                except Exception:
                    microphones.append({
                        'index': i,
                        'name': mic_name,
                        'available': False
                    })
            
            return microphones
            
        except Exception as e:
            logger.error(f"Failed to get microphone list: {e}")
            return []
    
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
                    logger.error(f"Error in voice recognition event listener: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recognition statistics"""
        return {
            **self.stats,
            'energy_threshold': self.recognizer.energy_threshold if self.recognizer else 0,
            'is_listening': self.is_listening,
            'is_paused': self.is_paused,
            'queue_size': self.command_queue.qsize()
        }

class VoiceManager:
    """Complete voice management system"""
    
    def __init__(self, config_manager=None):
        """
        Initialize Voice Manager
        
        Args:
            config_manager: Configuration manager for settings
        """
        self.config_manager = config_manager
        self.recognizer = None
        self.is_initialized = False
        self.listeners = {}
        
        # Load settings from config
        self.settings = self._load_settings()
        
        # Initialize recognizer
        self._initialize()
    
    def _load_settings(self) -> VoiceSettings:
        """Load voice settings from configuration"""
        if not self.config_manager:
            return VoiceSettings()
        
        try:
            return VoiceSettings(
                language=self.config_manager.get('voice.language', 'en-US'),
                energy_threshold=self.config_manager.get('voice.energy_threshold', 300.0),
                dynamic_energy_threshold=self.config_manager.get('voice.noise_reduction', True),
                pause_threshold=self.config_manager.get('voice.pause_threshold', 0.8),
                sample_rate=self.config_manager.get('voice.sample_rate', 16000)
            )
        except Exception as e:
            logger.warning(f"Failed to load voice settings: {e}")
            return VoiceSettings()
    
    def _initialize(self) -> bool:
        """Initialize the voice recognition system"""
        try:
            self.recognizer = VoiceRecognizer(self.settings)
            
            if self.recognizer.initialize():
                self.is_initialized = True
                logger.info("Voice Manager initialized successfully")
                return True
            else:
                logger.error("Failed to initialize voice recognizer")
                return False
                
        except Exception as e:
            logger.error(f"Voice Manager initialization error: {e}")
            return False
    
    def start_listening(self) -> bool:
        """Start continuous voice recognition"""
        if not self.is_initialized:
            logger.error("Voice Manager not initialized")
            return False
        
        return self.recognizer.start_listening()
    
    def stop_listening(self):
        """Stop voice recognition"""
        if self.recognizer:
            self.recognizer.stop_listening()
    
    def pause_listening(self):
        """Pause voice recognition"""
        if self.recognizer:
            self.recognizer.pause_listening()
    
    def resume_listening(self):
        """Resume voice recognition"""
        if self.recognizer:
            self.recognizer.resume_listening()
    
    def recognize_command(self, timeout: float = None) -> Optional[VoiceCommand]:
        """Recognize a single voice command"""
        if not self.is_initialized:
            return None
        
        return self.recognizer.recognize_once(timeout=timeout)
    
    def get_next_command(self, timeout: float = None) -> Optional[VoiceCommand]:
        """Get next command from recognition queue"""
        if not self.is_initialized:
            return None
        
        return self.recognizer.get_next_command(timeout=timeout)
    
    def calibrate_microphone(self, duration: float = 5.0) -> bool:
        """Calibrate microphone for ambient noise"""
        if not self.is_initialized:
            return False
        
        return self.recognizer.calibrate_microphone(duration)
    
    def get_microphone_list(self) -> List[Dict[str, Any]]:
        """Get available microphones"""
        if not self.is_initialized:
            return []
        
        return self.recognizer.get_microphone_list()
    
    def set_microphone(self, mic_index: int) -> bool:
        """Set active microphone"""
        if not self.is_initialized:
            return False
        
        try:
            self.settings.mic_index = mic_index
            self.recognizer.microphone = None  # Force reinitialization
            
            # Reinitialize microphone
            import speech_recognition as sr
            self.recognizer.microphone = sr.Microphone(device_index=mic_index)
            
            if self.recognizer._test_microphone():
                # Save to config
                if self.config_manager:
                    self.config_manager.set('voice.microphone_index', mic_index)
                
                logger.info(f"Microphone set to index {mic_index}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to set microphone: {e}")
            return False
    
    def add_command_listener(self, callback: Callable[[VoiceCommand], None]):
        """Add listener for recognized commands"""
        if self.recognizer:
            self.recognizer.add_listener('command_recognized', callback)
    
    def add_audio_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Add listener for audio data"""
        if self.recognizer:
            self.recognizer.add_listener('audio_data', callback)
    
    def get_audio_analysis(self) -> Dict[str, Any]:
        """Get current audio analysis"""
        if not self.is_initialized:
            return {}
        
        return self.recognizer.get_audio_analysis()
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice recognition status"""
        if not self.is_initialized:
            return {'initialized': False}
        
        return {
            'initialized': True,
            'is_listening': self.recognizer.is_listening,
            'is_paused': self.recognizer.is_paused,
            'statistics': self.recognizer.get_statistics(),
            'settings': {
                'language': self.settings.language,
                'energy_threshold': self.settings.energy_threshold,
                'microphone_index': self.settings.mic_index
            }
        }

# Global voice manager instance
_voice_manager = None

def get_voice_manager(config_manager=None) -> VoiceManager:
    """Get or create global voice manager"""
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = VoiceManager(config_manager)
    return _voice_manager

def start_voice_listening() -> bool:
    """Start voice recognition"""
    return get_voice_manager().start_listening()

def stop_voice_listening():
    """Stop voice recognition"""
    get_voice_manager().stop_listening()

def get_next_voice_command(timeout: float = None) -> Optional[VoiceCommand]:
    """Get next voice command"""
    return get_voice_manager().get_next_command(timeout)

def calibrate_microphone(duration: float = 5.0) -> bool:
    """Calibrate microphone"""
    return get_voice_manager().calibrate_microphone(duration)