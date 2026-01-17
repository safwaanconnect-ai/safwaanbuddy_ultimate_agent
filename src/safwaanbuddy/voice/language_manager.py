"""Multi-language configuration and management."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..core.config import ConfigManager


@dataclass
class Language:
    """Language configuration."""
    code: str
    name: str
    vosk_model: str
    tts_voice: Optional[str] = None


class LanguageManager:
    """Manage multi-language support."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        self.languages: Dict[str, Language] = {
            "en-US": Language(
                code="en-US",
                name="English (US)",
                vosk_model="vosk-model-en-us-0.22",
                tts_voice=None
            ),
            "en-IN": Language(
                code="en-IN",
                name="English (India)",
                vosk_model="vosk-model-en-in-0.5",
                tts_voice=None
            ),
            "hi-IN": Language(
                code="hi-IN",
                name="Hindi (India)",
                vosk_model="vosk-model-hi-0.22",
                tts_voice=None
            )
        }
        
        self.current_language = self.config.get("voice.default_language", "en-US")
    
    def get_language(self, code: str) -> Optional[Language]:
        """Get language by code.
        
        Args:
            code: Language code
            
        Returns:
            Language object or None
        """
        return self.languages.get(code)
    
    def set_language(self, code: str) -> bool:
        """Set current language.
        
        Args:
            code: Language code
            
        Returns:
            True if successful
        """
        if code not in self.languages:
            self.logger.error(f"Language not supported: {code}")
            return False
        
        self.current_language = code
        self.config.set("voice.default_language", code)
        self.logger.info(f"Language set to: {code}")
        return True
    
    def get_current_language(self) -> Language:
        """Get current language.
        
        Returns:
            Current Language object
        """
        return self.languages[self.current_language]
    
    def get_available_languages(self) -> List[Language]:
        """Get list of available languages.
        
        Returns:
            List of Language objects
        """
        return list(self.languages.values())
    
    def get_model_path(self, code: Optional[str] = None) -> Path:
        """Get Vosk model path for language.
        
        Args:
            code: Language code (uses current if None)
            
        Returns:
            Path to model directory
        """
        if code is None:
            code = self.current_language
        
        language = self.languages.get(code)
        if not language:
            self.logger.error(f"Language not found: {code}")
            return Path(self.config.get("voice.model_dir", "data/models/vosk"))
        
        base_dir = Path(self.config.get("voice.model_dir", "data/models/vosk"))
        return base_dir / language.vosk_model
    
    def is_model_downloaded(self, code: Optional[str] = None) -> bool:
        """Check if model is downloaded for language.
        
        Args:
            code: Language code (uses current if None)
            
        Returns:
            True if model exists
        """
        model_path = self.get_model_path(code)
        return model_path.exists() and (model_path / "am").exists()
    
    def get_download_url(self, code: Optional[str] = None) -> str:
        """Get download URL for language model.
        
        Args:
            code: Language code (uses current if None)
            
        Returns:
            Download URL
        """
        if code is None:
            code = self.current_language
        
        language = self.languages.get(code)
        if not language:
            return ""
        
        base_url = "https://alphacephei.com/vosk/models"
        return f"{base_url}/{language.vosk_model}.zip"
