#!/usr/bin/env python3
"""
Intent Evaluator for SafwanBuddy
NLP-based intent classification and command understanding
"""

import logging
import re
import json
import math
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
from fuzzywuzzy import fuzz, process
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Types of intents that can be recognized"""
    OPEN_APPLICATION = "open_application"
    WEB_SEARCH = "web_search"
    TYPE_TEXT = "type_text"
    CLICK_ELEMENT = "click_element"
    SYSTEM_STATUS = "system_status"
    WEATHER = "weather"
    TIME = "time"
    DATE = "date"
    MUSIC_CONTROL = "music_control"
    VOLUME_CONTROL = "volume_control"
    SCREENSHOT = "screenshot"
    WINDOW_MANAGEMENT = "window_management"
    FORM_FILLING = "form_filling"
    DOCUMENT_GENERATION = "document_generation"
    PRICE_COMPARISON = "price_comparison"
    CALL_CONTACT = "call_contact"
    MESSAGE_CONTACT = "message_contact"
    REMINDER_SET = "reminder_set"
    CALENDAR_QUERY = "calendar_query"
    FILE_MANAGEMENT = "file_management"
    BROWSER_CONTROL = "browser_control"
    EMAIL_CONTROL = "email_control"
    SYSTEM_SHUTDOWN = "system_shutdown"
    HELP_REQUEST = "help_request"
    UNKNOWN = "unknown"

@dataclass
class Intent:
    """Intent data structure"""
    type: IntentType
    confidence: float
    parameters: Dict[str, Any]
    original_text: str
    processed_text: str
    entities: List[str]
    suggestions: List[str] = None

class NaturalLanguageProcessor:
    """Core NLP processing for text analysis"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set()
        self.vocabulary = {}
        self.intent_patterns = {}
        
        # Initialize NLTK data
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """Initialize NLTK resources"""
        try:
            # Download required NLTK data
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            self.stop_words = set(stopwords.words('english'))
            logger.info("NLTK initialized successfully")
            
        except Exception as e:
            logger.warning(f"NLTK initialization failed: {e}. Using basic stop words.")
            self.stop_words = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
                'had', 'what', 'said', 'each', 'which', 'do', 'how', 'if', 'or',
                'about', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
                'her', 'would', 'make', 'like', 'into', 'him', 'time', 'has', 'two',
                'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been',
                'call', 'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did',
                'get', 'come', 'made', 'may', 'part'
            }
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text for analysis"""
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        try:
            tokens = word_tokenize(text)
        except:
            tokens = text.split()
        
        # Remove stop words and stem
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 1:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return processed_tokens
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        entities = []
        
        # Simple entity patterns
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        entities.extend(emails)
        
        # Phone numbers
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s?\d{3}[-.]?\d{4}',
            r'\+\d{1,3}[-.]?\d{10}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            entities.extend(phones)
        
        # URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        entities.extend(urls)
        
        # File paths
        path_patterns = [
            r'[/\\][^/\\:*?"<>|]+[/\\]?',
            r'[A-Za-z]:\\[^\\:*?"<>|]+',
        ]
        for pattern in path_patterns:
            paths = re.findall(pattern, text)
            entities.extend(paths)
        
        # Numbers
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        entities.extend(numbers)
        
        return list(set(entities))  # Remove duplicates

class IntentClassifier:
    """Intent classification using patterns and machine learning"""
    
    def __init__(self, nlp_processor: NaturalLanguageProcessor):
        self.nlp = nlp_processor
        self.intent_patterns = self._load_intent_patterns()
        self.command_variations = self._load_command_variations()
        self.application_names = self._load_application_names()
        self.web_services = self._load_web_services()
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load intent patterns for matching"""
        return {
            IntentType.OPEN_APPLICATION: [
                r'open\s+(\w+)',
                r'start\s+(\w+)',
                r'launch\s+(\w+)',
                r'run\s+(\w+)',
                r'activate\s+(\w+)',
                r'begin\s+(\w+)',
                r'fire\s+up\s+(\w+)',
                r'boot\s+(\w+)'
            ],
            IntentType.WEB_SEARCH: [
                r'search\s+for\s+(.+)',
                r'google\s+(.+)',
                r'look\s+up\s+(.+)',
                r'find\s+(.+)',
                r'web\s+search\s+(.+)',
                r'internet\s+search\s+(.+)',
                r'surf\s+for\s+(.+)',
                r'bing\s+(.+)',
                r'yahoo\s+(.+)'
            ],
            IntentType.TYPE_TEXT: [
                r'type\s+(.+)',
                r'write\s+(.+)',
                r'input\s+(.+)',
                r'enter\s+(.+)',
                r'fill\s+(.+)',
                r'key\s+(.+)',
                r'text\s+(.+)'
            ],
            IntentType.CLICK_ELEMENT: [
                r'click\s+(.+)',
                r'select\s+(.+)',
                r'press\s+(.+)',
                r'tap\s+(.+)',
                r'activate\s+(.+)',
                r'hit\s+(.+)',
                r'trigger\s+(.+)'
            ],
            IntentType.SYSTEM_STATUS: [
                r'system\s+status',
                r'computer\s+status',
                r'pc\s+status',
                r'how\s+is\s+(?:the\s+)?system',
                r'performance',
                r'system\s+info',
                r'computer\s+info'
            ],
            IntentType.WEATHER: [
                r'weather\s+in\s+(\w+)',
                r'weather\s+for\s+(\w+)',
                r'temperature\s+in\s+(\w+)',
                r'forecast\s+for\s+(\w+)',
                r'how\s+is\s+the\s+weather',
                r'weather\s+report'
            ],
            IntentType.TIME: [
                r'what\s+time\s+is\s+it',
                r'current\s+time',
                r'time\s+now',
                r'clock\s+time',
                r'tell\s+me\s+the\s+time'
            ],
            IntentType.DATE: [
                r'what\s+date\s+is\s+it',
                r'current\s+date',
                r'date\s+today',
                r'calendar\s+date',
                r'today\'s\s+date'
            ],
            IntentType.MUSIC_CONTROL: [
                r'play\s+music',
                r'play\s+song',
                r'play\s+(.+)',
                r'pause\s+music',
                r'stop\s+music',
                r'next\s+song',
                r'previous\s+song',
                r'skip\s+song',
                r'volume\s+up\s+music',
                r'volume\s+down\s+music'
            ],
            IntentType.VOLUME_CONTROL: [
                r'volume\s+up',
                r'volume\s+down',
                r'increase\s+volume',
                r'decrease\s+volume',
                r'mute\s+audio',
                r'unmute\s+audio',
                r'set\s+volume\s+to\s+(\d+)',
                r'volume\s+(\d+)'
            ],
            IntentType.SCREENSHOT: [
                r'take\s+screenshot',
                r'capture\s+screen',
                r'screenshot',
                r'grab\s+screen',
                r'picture\s+of\s+screen'
            ],
            IntentType.WINDOW_MANAGEMENT: [
                r'minimize\s+window',
                r'maximize\s+window',
                r'restore\s+window',
                r'close\s+window',
                r'switch\s+window',
                r'next\s+window',
                r'previous\s+window'
            ],
            IntentType.FORM_FILLING: [
                r'fill\s+form',
                r'complete\s+form',
                r'enter\s+information',
                r'populate\s+fields',
                r'fill\s+out\s+form'
            ],
            IntentType.DOCUMENT_GENERATION: [
                r'create\s+document',
                r'generate\s+document',
                r'make\s+document',
                r'write\s+document',
                r'new\s+document',
                r'document\s+generator'
            ],
            IntentType.PRICE_COMPARISON: [
                r'compare\s+price',
                r'price\s+comparison',
                r'cheapest\s+(.+)',
                r'best\s+price\s+for\s+(.+)',
                r'cost\s+of\s+(.+)',
                r'price\s+of\s+(.+)'
            ],
            IntentType.CALL_CONTACT: [
                r'call\s+(.+)',
                r'phone\s+(.+)',
                r'dial\s+(.+)',
                r'ring\s+(.+)',
                r'contact\s+(.+)'
            ],
            IntentType.MESSAGE_CONTACT: [
                r'send\s+message\s+to\s+(.+)',
                r'text\s+(.+)',
                r'sms\s+(.+)',
                r'whatsapp\s+(.+)',
                r'message\s+(.+)'
            ],
            IntentType.REMINDER_SET: [
                r'set\s+reminder',
                r'remind\s+me',
                r'create\s+reminder',
                r'add\s+reminder',
                r'schedule\s+reminder'
            ],
            IntentType.CALENDAR_QUERY: [
                r'what\'s\s+on\s+my\s+calendar',
                r'calendar\s+for\s+(.+)',
                r'appointments\s+(\w+)',
                r'schedule\s+today',
                r'what\'s\s+scheduled'
            ],
            IntentType.FILE_MANAGEMENT: [
                r'open\s+file',
                r'create\s+file',
                r'delete\s+file',
                r'move\s+file',
                r'copy\s+file',
                r'rename\s+file',
                r'file\s+manager'
            ],
            IntentType.BROWSER_CONTROL: [
                r'open\s+website',
                r'go\s+to\s+(.+)',
                r'navigate\s+to\s+(.+)',
                r'browse\s+(.+)',
                r'visit\s+(.+)',
                r'load\s+(.+)'
            ],
            IntentType.EMAIL_CONTROL: [
                r'check\s+email',
                r'send\s+email',
                r'compose\s+email',
                r'read\s+email',
                r'gmail',
                r'outlook',
                r'email\s+client'
            ],
            IntentType.SYSTEM_SHUTDOWN: [
                r'shutdown\s+computer',
                r'turn\s+off\s+computer',
                r'shut\s+down',
                r'power\s+off',
                r'log\s+off',
                r'restart\s+computer'
            ],
            IntentType.HELP_REQUEST: [
                r'help',
                r'what\s+can\s+you\s+do',
                r'commands',
                r'assistance',
                r'how\s+to\s+use',
                r'guide'
            ]
        }
    
    def _load_command_variations(self) -> Dict[str, List[str]]:
        """Load command variations for fuzzy matching"""
        return {
            "open": ["open", "start", "launch", "run", "activate", "begin", "fire up", "boot"],
            "search": ["search", "google", "look up", "find", "web search", "internet search", "surf"],
            "type": ["type", "write", "input", "enter", "fill", "key"],
            "click": ["click", "select", "press", "tap", "activate", "hit", "trigger"],
            "screenshot": ["screenshot", "capture screen", "grab screen", "picture of screen"],
            "weather": ["weather", "temperature", "forecast", "climate"],
            "time": ["time", "clock", "hour", "minute"],
            "date": ["date", "calendar", "day"],
            "music": ["music", "song", "audio", "play"],
            "volume": ["volume", "audio", "sound", "mute"],
            "window": ["window", "application", "program"],
            "form": ["form", "fill", "complete", "populate"],
            "document": ["document", "file", "create", "generate", "write"],
            "price": ["price", "cost", "money", "compare", "cheapest"],
            "call": ["call", "phone", "dial", "ring"],
            "message": ["message", "text", "sms", "whatsapp"],
            "reminder": ["reminder", "alarm", "note", "schedule"],
            "calendar": ["calendar", "schedule", "appointment", "event"],
            "file": ["file", "folder", "directory", "document"],
            "browser": ["browser", "web", "internet", "website"],
            "email": ["email", "gmail", "outlook", "mail"],
            "shutdown": ["shutdown", "power off", "turn off", "restart"]
        }
    
    def _load_application_names(self) -> Dict[str, List[str]]:
        """Load common application names"""
        return {
            "firefox": ["firefox", "mozilla", "browser"],
            "chrome": ["chrome", "google chrome", "browser"],
            "edge": ["edge", "microsoft edge", "browser"],
            "notepad": ["notepad", "text editor", "note"],
            "word": ["word", "microsoft word", "document"],
            "excel": ["excel", "microsoft excel", "spreadsheet"],
            "powerpoint": ["powerpoint", "presentation", "slides"],
            "calculator": ["calculator", "calc"],
            "paint": ["paint", "mspaint", "drawing"],
            "photoshop": ["photoshop", "adobe photoshop", "image editor"],
            "vlc": ["vlc", "media player", "video player"],
            "spotify": ["spotify", "music player"],
            "discord": ["discord", "chat"],
            "skype": ["skype", "video call"],
            "teams": ["teams", "microsoft teams", "meeting"],
            "zoom": ["zoom", "video conference"],
            "steam": ["steam", "gaming platform"],
            "git": ["git", "github", "version control"],
            "pycharm": ["pycharm", "python ide"],
            "vscode": ["vscode", "visual studio code", "code editor"],
            "android studio": ["android studio", "android ide"],
            "eclipse": ["eclipse", "java ide"],
            "postman": ["postman", "api testing"],
            "slack": ["slack", "team chat"],
            "telegram": ["telegram", "messaging"]
        }
    
    def _load_web_services(self) -> Dict[str, List[str]]:
        """Load common web services"""
        return {
            "google": ["google", "search engine"],
            "youtube": ["youtube", "video sharing"],
            "facebook": ["facebook", "social media"],
            "twitter": ["twitter", "tweet"],
            "instagram": ["instagram", "photos"],
            "linkedin": ["linkedin", "professional"],
            "reddit": ["reddit", "forums"],
            "wikipedia": ["wikipedia", "encyclopedia"],
            "github": ["github", "code repository"],
            "stackoverflow": ["stackoverflow", "programming help"],
            "amazon": ["amazon", "shopping"],
            "ebay": ["ebay", "auction"],
            "netflix": ["netflix", "streaming"],
            "spotify": ["spotify", "music streaming"],
            "discord": ["discord", "gaming chat"],
            "twitch": ["twitch", "gaming stream"]
        }
    
    def classify_intent(self, text: str) -> Intent:
        """Classify intent from text"""
        if not text or not text.strip():
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                original_text="",
                processed_text="",
                entities=[]
            )
        
        original_text = text.strip()
        processed_tokens = self.nlp.preprocess_text(original_text)
        entities = self.nlp.extract_entities(original_text)
        
        # Pattern matching
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = re.findall(pattern, original_text, re.IGNORECASE)
                if matches:
                    # Give higher score for exact pattern matches
                    score += 0.8
                    # Additional score for capturing groups
                    if len(matches[0]) > 0:
                        score += 0.2
                    break
            intent_scores[intent_type] = score
        
        # Fuzzy matching for command variations
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                # Extract keywords from pattern
                keywords = re.findall(r'\b\w+\b', pattern)
                for keyword in keywords:
                    if keyword in ["r", "s", "for", "the", "to", "of", "in", "on", "at"]:
                        continue
                    
                    # Get variations for this keyword
                    if keyword in self.command_variations:
                        variations = self.command_variations[keyword]
                        for variation in variations:
                            ratio = fuzz.partial_ratio(variation.lower(), original_text.lower())
                            if ratio > 70:  # Threshold for fuzzy match
                                intent_scores[intent_type] = intent_scores.get(intent_type, 0) + (ratio / 100.0) * 0.5
        
        # Find the best matching intent
        if intent_scores:
            best_intent_type = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent_type]
            
            # Normalize score to 0-1 range
            confidence = min(1.0, best_score)
            
            # Extract parameters
            parameters = self._extract_parameters(best_intent_type, original_text)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(best_intent_type, original_text)
            
            return Intent(
                type=best_intent_type,
                confidence=confidence,
                parameters=parameters,
                original_text=original_text,
                processed_text=" ".join(processed_tokens),
                entities=entities,
                suggestions=suggestions
            )
        else:
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                original_text=original_text,
                processed_text=" ".join(processed_tokens),
                entities=entities
            )
    
    def _extract_parameters(self, intent_type: IntentType, text: str) -> Dict[str, Any]:
        """Extract parameters from text based on intent type"""
        parameters = {}
        
        try:
            if intent_type == IntentType.OPEN_APPLICATION:
                # Extract application name
                for app_name, aliases in self.application_names.items():
                    for alias in aliases:
                        if fuzz.partial_ratio(alias.lower(), text.lower()) > 80:
                            parameters['application'] = app_name
                            break
                    if 'application' in parameters:
                        break
                
                # Also extract from regex patterns
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        parameters['application'] = matches[0]
                        break
            
            elif intent_type == IntentType.WEB_SEARCH:
                # Extract search query
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        parameters['query'] = matches[0]
                        break
            
            elif intent_type == IntentType.TYPE_TEXT:
                # Extract text to type
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        parameters['text'] = matches[0]
                        break
            
            elif intent_type == IntentType.WEATHER:
                # Extract location
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        parameters['location'] = matches[0]
                        break
            
            elif intent_type == IntentType.CALL_CONTACT or intent_type == IntentType.MESSAGE_CONTACT:
                # Extract contact name
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        parameters['contact'] = matches[0]
                        break
            
            elif intent_type == IntentType.VOLUME_CONTROL:
                # Extract volume level
                volume_patterns = [r'set\s+volume\s+to\s+(\d+)', r'volume\s+(\d+)']
                for pattern in volume_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        try:
                            parameters['level'] = int(matches[0])
                            break
                        except ValueError:
                            pass
            
            elif intent_type == IntentType.PRICE_COMPARISON:
                # Extract product name
                patterns = self.intent_patterns[intent_type]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        parameters['product'] = matches[0]
                        break
            
            # Always include entities found in text
            if self.nlp.extract_entities(text):
                parameters['entities'] = self.nlp.extract_entities(text)
                
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
        
        return parameters
    
    def _generate_suggestions(self, intent_type: IntentType, text: str) -> List[str]:
        """Generate suggestions for the user"""
        suggestions = []
        
        try:
            if intent_type == IntentType.OPEN_APPLICATION:
                # Suggest common applications
                suggestions = [
                    "Try saying 'open Firefox'",
                    "Try saying 'launch Chrome'", 
                    "Try saying 'start Notepad'"
                ]
            
            elif intent_type == IntentType.WEB_SEARCH:
                suggestions = [
                    "Try saying 'search for Python tutorials'",
                    "Try saying 'google machine learning'",
                    "Try saying 'look up weather in New York'"
                ]
            
            elif intent_type == IntentType.WEATHER:
                suggestions = [
                    "Try saying 'weather in London'",
                    "Try saying 'temperature in Paris'",
                    "Try saying 'forecast for Tokyo'"
                ]
            
            elif intent_type == IntentType.HELP_REQUEST:
                suggestions = [
                    "I can help you open applications",
                    "I can search the web for you",
                    "I can take screenshots",
                    "I can control your music",
                    "I can check the weather",
                    "I can tell you the time and date"
                ]
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
        
        return suggestions

class IntentEvaluator:
    """Main intent evaluation system"""
    
    def __init__(self, config_manager=None):
        """
        Initialize Intent Evaluator
        
        Args:
            config_manager: Configuration manager for settings
        """
        self.config_manager = config_manager
        self.nlp_processor = NaturalLanguageProcessor()
        self.classifier = IntentClassifier(self.nlp_processor)
        
        # Learning and adaptation
        self.feedback_history = []
        self.adapted_patterns = {}
        
        logger.info("Intent Evaluator initialized")
    
    def evaluate_intent(self, text: str) -> Intent:
        """
        Evaluate intent from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Intent object with classification results
        """
        if not text or not text.strip():
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                original_text="",
                processed_text="",
                entities=[]
            )
        
        try:
            # Clean input
            text = text.strip()
            
            # Classify intent
            intent = self.classifier.classify_intent(text)
            
            # Apply confidence thresholds
            if intent.confidence < 0.3:
                intent.type = IntentType.UNKNOWN
                intent.confidence = 0.0
            
            # Learn from context if confidence is low
            if intent.confidence < 0.6:
                intent = self._apply_contextual_learning(text, intent)
            
            # Add helpful suggestions for unknown intents
            if intent.type == IntentType.UNKNOWN:
                intent.suggestions = self._generate_fallback_suggestions(text)
            
            logger.info(f"Intent classified: {intent.type.value} (confidence: {intent.confidence:.2f})")
            
            return intent
            
        except Exception as e:
            logger.error(f"Intent evaluation error: {e}")
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                original_text=text,
                processed_text="",
                entities=[]
            )
    
    def _apply_contextual_learning(self, text: str, intent: Intent) -> Intent:
        """Apply contextual learning to improve intent recognition"""
        try:
            # Simple contextual analysis
            context_keywords = {
                'application': ['app', 'program', 'software', 'application'],
                'web': ['web', 'internet', 'online', 'browser', 'search'],
                'system': ['computer', 'system', 'pc', 'status'],
                'media': ['music', 'video', 'audio', 'player'],
                'communication': ['call', 'message', 'email', 'contact']
            }
            
            text_lower = text.lower()
            
            # Find contextual clues
            for context, keywords in context_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    # Adjust intent based on context
                    if context == 'application' and intent.type == IntentType.UNKNOWN:
                        intent.type = IntentType.OPEN_APPLICATION
                        intent.confidence = max(intent.confidence, 0.5)
                    elif context == 'web' and intent.type == IntentType.UNKNOWN:
                        intent.type = IntentType.WEB_SEARCH
                        intent.confidence = max(intent.confidence, 0.5)
                    elif context == 'media' and intent.type == IntentType.UNKNOWN:
                        intent.type = IntentType.MUSIC_CONTROL
                        intent.confidence = max(intent.confidence, 0.5)
                    elif context == 'system' and intent.type == IntentType.UNKNOWN:
                        intent.type = IntentType.SYSTEM_STATUS
                        intent.confidence = max(intent.confidence, 0.5)
            
            return intent
            
        except Exception as e:
            logger.error(f"Contextual learning error: {e}")
            return intent
    
    def _generate_fallback_suggestions(self, text: str) -> List[str]:
        """Generate suggestions when intent cannot be determined"""
        suggestions = [
            "I didn't understand that command. Here are some things I can do:",
            "• Open applications: 'Open Firefox'",
            "• Search the web: 'Search for Python tutorials'",
            "• Take screenshots: 'Take a screenshot'",
            "• Check weather: 'Weather in London'",
            "• Tell time: 'What time is it?'",
            "• Control music: 'Play music'",
            "• System info: 'System status'"
        ]
        
        return suggestions
    
    def provide_feedback(self, text: str, predicted_intent: Intent, user_correction: IntentType):
        """Provide feedback to improve future predictions"""
        try:
            feedback = {
                'text': text,
                'predicted_intent': predicted_intent.type,
                'predicted_confidence': predicted_intent.confidence,
                'correct_intent': user_correction,
                'timestamp': time.time()
            }
            
            self.feedback_history.append(feedback)
            
            # Update patterns based on feedback (simple adaptation)
            if predicted_intent.type != user_correction:
                self._update_patterns_from_feedback(text, user_correction)
            
            logger.debug(f"Feedback recorded: {text} -> {user_correction.value}")
            
        except Exception as e:
            logger.error(f"Feedback processing error: {e}")
    
    def _update_patterns_from_feedback(self, text: str, correct_intent: IntentType):
        """Update patterns based on user feedback"""
        try:
            # Extract keywords from the text
            keywords = self.nlp_processor.preprocess_text(text)
            
            # Store feedback for future reference
            if correct_intent not in self.adapted_patterns:
                self.adapted_patterns[correct_intent] = []
            
            self.adapted_patterns[correct_intent].append({
                'keywords': keywords,
                'original_text': text,
                'frequency': 1
            })
            
        except Exception as e:
            logger.error(f"Pattern update error: {e}")
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent types"""
        return [intent_type.value for intent_type in IntentType]
    
    def get_intent_description(self, intent_type: IntentType) -> str:
        """Get description of what an intent type does"""
        descriptions = {
            IntentType.OPEN_APPLICATION: "Open or launch applications",
            IntentType.WEB_SEARCH: "Search the web for information",
            IntentType.TYPE_TEXT: "Type text into active applications",
            IntentType.CLICK_ELEMENT: "Click on UI elements",
            IntentType.SYSTEM_STATUS: "Get system information and status",
            IntentType.WEATHER: "Get weather information",
            IntentType.TIME: "Get current time",
            IntentType.DATE: "Get current date",
            IntentType.MUSIC_CONTROL: "Control music playback",
            IntentType.VOLUME_CONTROL: "Control system volume",
            IntentType.SCREENSHOT: "Take screenshots",
            IntentType.WINDOW_MANAGEMENT: "Manage application windows",
            IntentType.FORM_FILLING: "Fill out forms automatically",
            IntentType.DOCUMENT_GENERATION: "Generate documents",
            IntentType.PRICE_COMPARISON: "Compare prices online",
            IntentType.CALL_CONTACT: "Make phone calls",
            IntentType.MESSAGE_CONTACT: "Send messages",
            IntentType.REMINDER_SET: "Set reminders",
            IntentType.CALENDAR_QUERY: "Check calendar",
            IntentType.FILE_MANAGEMENT: "Manage files and folders",
            IntentType.BROWSER_CONTROL: "Control web browser",
            IntentType.EMAIL_CONTROL: "Control email client",
            IntentType.SYSTEM_SHUTDOWN: "Shutdown or restart computer",
            IntentType.HELP_REQUEST: "Get help and assistance",
            IntentType.UNKNOWN: "Unknown or unclassified intent"
        }
        
        return descriptions.get(intent_type, "No description available")
    
    def test_intent_recognition(self) -> Dict[str, float]:
        """Test intent recognition accuracy with sample data"""
        test_cases = [
            ("open firefox", IntentType.OPEN_APPLICATION),
            ("search for python tutorials", IntentType.WEB_SEARCH),
            ("what time is it", IntentType.TIME),
            ("take a screenshot", IntentType.SCREENSHOT),
            ("play music", IntentType.MUSIC_CONTROL),
            ("system status", IntentType.SYSTEM_STATUS),
            ("weather in london", IntentType.WEATHER),
            ("volume up", IntentType.VOLUME_CONTROL),
            ("call john", IntentType.CALL_CONTACT),
            ("send message to sarah", IntentType.MESSAGE_CONTACT)
        ]
        
        correct_predictions = 0
        total_predictions = len(test_cases)
        
        for test_input, expected_intent in test_cases:
            result = self.evaluate_intent(test_input)
            if result.type == expected_intent and result.confidence > 0.3:
                correct_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        logger.info(f"Intent recognition test accuracy: {accuracy:.2%}")
        
        return {
            'accuracy': accuracy,
            'correct_predictions': correct_predictions,
            'total_predictions': total_predictions
        }

# Global intent evaluator instance
_intent_evaluator = None

def get_intent_evaluator(config_manager=None) -> IntentEvaluator:
    """Get or create global intent evaluator"""
    global _intent_evaluator
    if _intent_evaluator is None:
        _intent_evaluator = IntentEvaluator(config_manager)
    return _intent_evaluator

def evaluate_text_intent(text: str) -> Intent:
    """Evaluate intent from text"""
    return get_intent_evaluator().evaluate_intent(text)

def get_supported_intents() -> List[str]:
    """Get supported intent types"""
    return get_intent_evaluator().get_supported_intents()