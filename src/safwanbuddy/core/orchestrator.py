#!/usr/bin/env python3
"""
SafwanBuddy Orchestrator - Main Command Processing System
Coordinates all components and handles command execution
"""

import logging
import threading
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import asdict
from enum import Enum

# Import core components
from .intent_evaluator import IntentEvaluator, Intent, IntentType
from .voice_manager import VoiceManager, VoiceCommand
from .tts_manager import TTSManager
from .event_bus import EventBus
from ..automation.desktop_executor import DesktopExecutor
from ..profiles.profile_manager import ProfileManager
from .config import ConfigManager
from .logging import get_command_logger, get_performance_logger

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CommandExecution:
    """Command execution tracking"""
    command_id: str
    intent: Intent
    start_time: float
    end_time: Optional[float] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0

class SafwanBuddyOrchestrator:
    """
    Main orchestrator that coordinates all SafwanBuddy components
    Processes voice commands and executes appropriate actions
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        event_bus: EventBus,
        profile_manager: ProfileManager
    ):
        """
        Initialize the orchestrator
        
        Args:
            config_manager: Configuration manager
            event_bus: Event bus for inter-component communication
            profile_manager: Profile manager for user data
        """
        self.config_manager = config_manager
        self.event_bus = event_bus
        self.profile_manager = profile_manager
        
        # Initialize core components
        self.voice_manager = VoiceManager(config_manager)
        self.tts_manager = TTSManager(config_manager)
        self.intent_evaluator = IntentEvaluator(config_manager)
        self.desktop_executor = DesktopExecutor(config_manager)
        
        # Command execution tracking
        self.active_executions: Dict[str, CommandExecution] = {}
        self.execution_history: List[CommandExecution] = []
        self.command_counter = 0
        
        # System state
        self.is_running = False
        self.is_paused = False
        self.auto_listen = True
        
        # Performance tracking
        self.performance_logger = get_performance_logger()
        self.command_logger = get_command_logger()
        
        # Event handlers
        self._setup_event_handlers()
        
        # Statistics
        self.stats = {
            'commands_processed': 0,
            'commands_succeeded': 0,
            'commands_failed': 0,
            'total_execution_time': 0.0,
            'average_response_time': 0.0
        }
        
        logger.info("SafwanBuddy Orchestrator initialized")
    
    def _setup_event_handlers(self):
        """Set up event handlers for component communication"""
        try:
            # Voice command events
            if hasattr(self.voice_manager, 'add_command_listener'):
                self.voice_manager.add_command_listener(self._on_voice_command)
            
            # TTS events
            if hasattr(self.tts_manager, 'add_listener'):
                self.tts_manager.add_listener('speech_completed', self._on_speech_completed)
                self.tts_manager.add_listener('speech_error', self._on_speech_error)
            
            # System events
            self.event_bus.subscribe('shutdown_request', self._on_shutdown_request)
            self.event_bus.subscribe('pause_orchestrator', self._on_pause_request)
            self.event_bus.subscribe('resume_orchestrator', self._on_resume_request)
            
            logger.info("Event handlers configured")
            
        except Exception as e:
            logger.error(f"Error setting up event handlers: {e}")
    
    def start(self) -> bool:
        """Start the orchestrator and all subsystems"""
        try:
            logger.info("Starting SafwanBuddy Orchestrator...")
            
            # Initialize components
            if not self._initialize_components():
                return False
            
            # Start voice recognition
            if not self.voice_manager.start_listening():
                logger.warning("Failed to start voice recognition, continuing without it")
            
            # Start TTS
            if not self.tts_manager.speak("SafwanBuddy is ready to assist you.", blocking=False):
                logger.warning("Failed to initialize TTS")
            
            # Start event processing
            self.event_bus.start_processing()
            
            self.is_running = True
            self.is_paused = False
            
            # Emit startup event
            self.event_bus.emit('orchestrator_started', {
                'timestamp': time.time(),
                'components': self._get_active_components()
            })
            
            logger.info("SafwanBuddy Orchestrator started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start orchestrator: {e}")
            return False
    
    def stop(self):
        """Stop the orchestrator and all subsystems"""
        try:
            logger.info("Stopping SafwanBuddy Orchestrator...")
            
            self.is_running = False
            self.is_paused = False
            
            # Stop voice recognition
            self.voice_manager.stop_listening()
            
            # Stop any active TTS
            self.tts_manager.stop()
            
            # Cancel active executions
            for execution in list(self.active_executions.values()):
                self._cancel_execution(execution.command_id)
            
            # Stop event processing
            self.event_bus.stop_processing()
            
            # Emit shutdown event
            self.event_bus.emit('orchestrator_stopped', {
                'timestamp': time.time(),
                'statistics': self.stats.copy()
            })
            
            logger.info("SafwanBuddy Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping orchestrator: {e}")
    
    def pause(self):
        """Pause orchestrator (stop processing new commands)"""
        self.is_paused = True
        self.voice_manager.pause_listening()
        
        self.event_bus.emit('orchestrator_paused', {'timestamp': time.time()})
        logger.info("Orchestrator paused")
    
    def resume(self):
        """Resume orchestrator after pause"""
        self.is_paused = False
        self.voice_manager.resume_listening()
        
        self.event_bus.emit('orchestrator_resumed', {'timestamp': time.time()})
        logger.info("Orchestrator resumed")
    
    def process_command(self, text: str, source: str = "manual") -> Optional[CommandExecution]:
        """
        Process a text command
        
        Args:
            text: Command text to process
            source: Source of the command (voice, text, api, etc.)
            
        Returns:
            CommandExecution object or None
        """
        if not text or not text.strip():
            return None
        
        self.performance_logger.start_timer(f"command_processing_{source}")
        
        try:
            # Create command ID
            self.command_counter += 1
            command_id = f"cmd_{self.command_counter}_{int(time.time())}"
            
            # Evaluate intent
            intent = self.intent_evaluator.evaluate_intent(text)
            
            # Create execution tracking
            execution = CommandExecution(
                command_id=command_id,
                intent=intent,
                start_time=time.time()
            )
            
            self.active_executions[command_id] = execution
            
            # Log command
            self.command_logger.log_command(text, source, intent.confidence)
            
            # Check confidence threshold
            if intent.confidence < 0.3:
                self._handle_low_confidence(text, intent, execution)
                return execution
            
            # Process based on intent type
            self._execute_intent(intent, execution)
            
            # Update statistics
            self.stats['commands_processed'] += 1
            
            return execution
            
        except Exception as e:
            logger.error(f"Error processing command '{text}': {e}")
            self._handle_execution_error(execution, str(e))
            return None
        finally:
            self.performance_logger.end_timer(f"command_processing_{source}")
    
    def _initialize_components(self) -> bool:
        """Initialize all components"""
        try:
            components_ok = True
            
            # Check voice manager
            if not self.voice_manager.is_initialized:
                logger.warning("Voice manager not initialized")
                components_ok = False
            
            # Check TTS manager
            if not self.tts_manager.is_initialized:
                logger.warning("TTS manager not initialized")
                # TTS is not critical, so continue
            
            # Check intent evaluator
            try:
                test_intent = self.intent_evaluator.evaluate_intent("test")
                if test_intent:
                    logger.info("Intent evaluator working")
                else:
                    logger.warning("Intent evaluator not working properly")
                    components_ok = False
            except Exception as e:
                logger.error(f"Intent evaluator error: {e}")
                components_ok = False
            
            # Check desktop executor
            try:
                if hasattr(self.desktop_executor, 'is_initialized'):
                    if not self.desktop_executor.is_initialized:
                        logger.warning("Desktop executor not initialized")
                        components_ok = False
            except Exception as e:
                logger.error(f"Desktop executor error: {e}")
                components_ok = False
            
            return components_ok
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            return False
    
    def _on_voice_command(self, voice_command: VoiceCommand):
        """Handle voice command from voice manager"""
        try:
            if self.is_paused or not self.is_running:
                return
            
            logger.info(f"Voice command received: {voice_command.text}")
            
            # Process the command
            execution = self.process_command(voice_command.text, "voice")
            
            if execution:
                execution.result = voice_command
                
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
    
    def _execute_intent(self, intent: Intent, execution: CommandExecution):
        """Execute the appropriate action based on intent"""
        execution.status = ExecutionStatus.RUNNING
        execution.progress = 0.1
        
        try:
            # Emit execution started event
            self.event_bus.emit('command_execution_started', {
                'command_id': execution.command_id,
                'intent_type': intent.type.value,
                'parameters': intent.parameters
            })
            
            # Route to appropriate handler
            handler_name = f"_handle_{intent.type.value}"
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                handler(intent, execution)
            else:
                self._handle_unknown_intent(intent, execution)
                
        except Exception as e:
            logger.error(f"Error executing intent {intent.type.value}: {e}")
            self._handle_execution_error(execution, str(e))
    
    def _handle_open_application(self, intent: Intent, execution: CommandExecution):
        """Handle open application intent"""
        try:
            app_name = intent.parameters.get('application', '')
            
            if not app_name:
                self.tts_manager.speak("I need to know which application to open.")
                execution.status = ExecutionStatus.FAILED
                execution.error = "No application specified"
                return
            
            # Speak confirmation
            self.tts_manager.speak(f"Opening {app_name}.")
            
            # Execute desktop action
            success = self.desktop_executor.open_application(app_name)
            
            if success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = f"Application {app_name} opened"
                execution.progress = 1.0
                
                # Log execution
                self.command_logger.log_execution(
                    f"open_application({app_name})",
                    "success",
                    time.time() - execution.start_time
                )
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = f"Failed to open {app_name}"
                
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_web_search(self, intent: Intent, execution: CommandExecution):
        """Handle web search intent"""
        try:
            query = intent.parameters.get('query', '')
            
            if not query:
                self.tts_manager.speak("What would you like me to search for?")
                execution.status = ExecutionStatus.FAILED
                return
            
            # Speak confirmation
            self.tts_manager.speak(f"Searching for {query}.")
            
            # Execute search
            success = self.desktop_executor.search_web(query)
            
            if success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = f"Search completed for: {query}"
                execution.progress = 1.0
                
                self.command_logger.log_execution(
                    f"web_search({query})",
                    "success",
                    time.time() - execution.start_time
                )
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = f"Search failed for: {query}"
                
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_type_text(self, intent: Intent, execution: CommandExecution):
        """Handle type text intent"""
        try:
            text = intent.parameters.get('text', '')
            
            if not text:
                self.tts_manager.speak("What text would you like me to type?")
                execution.status = ExecutionStatus.FAILED
                return
            
            # Speak confirmation
            self.tts_manager.speak(f"Typing: {text}")
            
            # Execute typing
            success = self.desktop_executor.type_text(text)
            
            if success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = f"Text typed: {text[:50]}{'...' if len(text) > 50 else ''}"
                execution.progress = 1.0
                
                self.command_logger.log_execution(
                    f"type_text({text[:20]}...)",
                    "success",
                    time.time() - execution.start_time
                )
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = f"Failed to type text: {text[:20]}..."
                
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_click_element(self, intent: Intent, execution: CommandExecution):
        """Handle click element intent"""
        try:
            element = intent.parameters.get('element', '')
            
            if not element:
                self.tts_manager.speak("What would you like me to click on?")
                execution.status = ExecutionStatus.FAILED
                return
            
            # Speak confirmation
            self.tts_manager.speak(f"Clicking on {element}.")
            
            # Execute click
            success = self.desktop_executor.click_element(element)
            
            if success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = f"Clicked on: {element}"
                execution.progress = 1.0
                
                self.command_logger.log_execution(
                    f"click_element({element})",
                    "success",
                    time.time() - execution.start_time
                )
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = f"Failed to click on: {element}"
                
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_system_status(self, intent: Intent, execution: CommandExecution):
        """Handle system status intent"""
        try:
            # Get system information
            system_info = self._get_system_status()
            
            # Format response
            response = f"System status: CPU usage {system_info['cpu']:.1f}%, "
            response += f"Memory usage {system_info['memory']:.1f}%, "
            response += f"Active applications: {system_info['apps']}"
            
            # Speak response
            self.tts_manager.speak(response)
            
            execution.status = ExecutionStatus.COMPLETED
            execution.result = system_info
            execution.progress = 1.0
            
            self.command_logger.log_execution(
                "system_status",
                "success",
                time.time() - execution.start_time
            )
            
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_time(self, intent: Intent, execution: CommandExecution):
        """Handle time query intent"""
        try:
            from datetime import datetime
            
            current_time = datetime.now().strftime("%I:%M %p")
            
            response = f"The current time is {current_time}"
            self.tts_manager.speak(response)
            
            execution.status = ExecutionStatus.COMPLETED
            execution.result = current_time
            execution.progress = 1.0
            
            self.command_logger.log_execution(
                "time_query",
                "success",
                time.time() - execution.start_time
            )
            
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_date(self, intent: Intent, execution: CommandExecution):
        """Handle date query intent"""
        try:
            from datetime import datetime
            
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            
            response = f"Today is {current_date}"
            self.tts_manager.speak(response)
            
            execution.status = ExecutionStatus.COMPLETED
            execution.result = current_date
            execution.progress = 1.0
            
            self.command_logger.log_execution(
                "date_query",
                "success",
                time.time() - execution.start_time
            )
            
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_screenshot(self, intent: Intent, execution: CommandExecution):
        """Handle screenshot intent"""
        try:
            # Speak confirmation
            self.tts_manager.speak("Taking a screenshot.")
            
            # Execute screenshot
            screenshot_path = self.desktop_executor.take_screenshot()
            
            if screenshot_path:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = f"Screenshot saved to: {screenshot_path}"
                execution.progress = 1.0
                
                self.command_logger.log_execution(
                    "take_screenshot",
                    "success",
                    time.time() - execution.start_time
                )
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = "Failed to take screenshot"
                
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_volume_control(self, intent: Intent, execution: CommandExecution):
        """Handle volume control intent"""
        try:
            level = intent.parameters.get('level')
            action = "up" if level is None else f"set to {level}"
            
            if level is not None:
                success = self.desktop_executor.set_volume(level)
                response = f"Volume set to {level} percent"
            else:
                # Default volume up/down
                if "up" in intent.original_text.lower():
                    success = self.desktop_executor.volume_up()
                    response = "Volume increased"
                else:
                    success = self.desktop_executor.volume_down()
                    response = "Volume decreased"
            
            if success:
                self.tts_manager.speak(response)
                execution.status = ExecutionStatus.COMPLETED
                execution.result = response
                execution.progress = 1.0
                
                self.command_logger.log_execution(
                    f"volume_control({action})",
                    "success",
                    time.time() - execution.start_time
                )
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = f"Failed to control volume: {action}"
                
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_weather(self, intent: Intent, execution: CommandExecution):
        """Handle weather query intent"""
        try:
            location = intent.parameters.get('location', '')
            
            if location:
                response = f"Weather information for {location} is not available right now. "
                response += "Please check your weather app or website."
            else:
                response = "Please specify a location for weather information."
            
            self.tts_manager.speak(response)
            
            execution.status = ExecutionStatus.COMPLETED
            execution.result = response
            execution.progress = 1.0
            
            self.command_logger.log_execution(
                f"weather_query({location})",
                "success",
                time.time() - execution.start_time
            )
            
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_help_request(self, intent: Intent, execution: CommandExecution):
        """Handle help request intent"""
        try:
            help_text = """
            I can help you with various tasks including:
            
            Opening applications: 'Open Firefox', 'Start Chrome'
            Searching the web: 'Search for Python tutorials'
            Taking screenshots: 'Take a screenshot'
            System information: 'System status'
            Time and date: 'What time is it?', 'What date is it?'
            Volume control: 'Volume up', 'Volume down'
            Typing text: 'Type hello world'
            Clicking elements: 'Click on the search button'
            
            Just tell me what you'd like to do!
            """
            
            self.tts_manager.speak("I can help you with various tasks. Here's what I can do:")
            time.sleep(1)  # Pause between sentences
            self.tts_manager.speak("Open applications, search the web, take screenshots, check system status, tell time and date, control volume, type text, and click elements.")
            
            execution.status = ExecutionStatus.COMPLETED
            execution.result = help_text
            execution.progress = 1.0
            
            self.command_logger.log_execution(
                "help_request",
                "success",
                time.time() - execution.start_time
            )
            
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_unknown_intent(self, intent: Intent, execution: CommandExecution):
        """Handle unknown or unhandled intent"""
        try:
            response = "I didn't understand that command. "
            
            if intent.suggestions:
                # Use suggestions from intent evaluator
                self.tts_manager.speak(response + "Try saying something like " + intent.suggestions[0])
            else:
                response += "Please try rephrasing your request or say 'help' for assistance."
                self.tts_manager.speak(response)
            
            execution.status = ExecutionStatus.FAILED
            execution.error = "Unknown intent"
            execution.result = response
            
        except Exception as e:
            self._handle_execution_error(execution, str(e))
    
    def _handle_low_confidence(self, text: str, intent: Intent, execution: CommandExecution):
        """Handle commands with low confidence"""
        try:
            response = "I didn't quite catch that. Could you please repeat?"
            self.tts_manager.speak(response)
            
            execution.status = ExecutionStatus.FAILED
            execution.error = "Low confidence"
            execution.result = f"Low confidence: {intent.confidence:.2f}"
            
        except Exception as e:
            logger.error(f"Error handling low confidence: {e}")
    
    def _handle_execution_error(self, execution: CommandExecution, error: str):
        """Handle execution errors"""
        try:
            execution.status = ExecutionStatus.FAILED
            execution.end_time = time.time()
            execution.error = error
            
            # Update statistics
            self.stats['commands_failed'] += 1
            
            # Log error
            self.command_logger.log_execution(
                f"command_execution({execution.intent.type.value})",
                f"failed: {error}",
                execution.end_time - execution.start_time
            )
            
            # Emit error event
            self.event_bus.emit('command_execution_error', {
                'command_id': execution.command_id,
                'error': error,
                'intent_type': execution.intent.type.value
            })
            
            # Move to history
            self.execution_history.append(execution)
            if execution.command_id in self.active_executions:
                del self.active_executions[execution.command_id]
            
        except Exception as e:
            logger.error(f"Error handling execution error: {e}")
    
    def _cancel_execution(self, command_id: str):
        """Cancel an active execution"""
        if command_id in self.active_executions:
            execution = self.active_executions[command_id]
            execution.status = ExecutionStatus.CANCELLED
            execution.end_time = time.time()
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[command_id]
            
            logger.info(f"Cancelled execution: {command_id}")
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Count running applications (simplified)
            try:
                processes = len(psutil.pids())
            except:
                processes = 0
            
            return {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'disk': disk.percent,
                'apps': processes,
                'timestamp': time.time()
            }
            
        except ImportError:
            return {
                'cpu': 0.0,
                'memory': 0.0,
                'disk': 0.0,
                'apps': 0,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def _get_active_components(self) -> List[str]:
        """Get list of active components"""
        components = []
        
        if self.voice_manager.is_initialized:
            components.append('voice_manager')
        
        if hasattr(self.tts_manager, 'is_initialized') and self.tts_manager.is_initialized:
            components.append('tts_manager')
        
        components.append('intent_evaluator')
        components.append('desktop_executor')
        components.append('profile_manager')
        
        return components
    
    def _on_speech_completed(self, data: Dict[str, Any]):
        """Handle TTS speech completion"""
        logger.debug(f"TTS speech completed: {data.get('text', '')[:50]}...")
    
    def _on_speech_error(self, data: Dict[str, Any]):
        """Handle TTS speech errors"""
        logger.warning(f"TTS speech error: {data.get('error', 'Unknown error')}")
    
    def _on_shutdown_request(self, data: Dict[str, Any]):
        """Handle system shutdown request"""
        logger.info("Shutdown request received")
        self.stop()
    
    def _on_pause_request(self, data: Dict[str, Any]):
        """Handle pause request"""
        self.pause()
    
    def _on_resume_request(self, data: Dict[str, Any]):
        """Handle resume request"""
        self.resume()
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'active_executions': len(self.active_executions),
            'execution_history': len(self.execution_history),
            'statistics': self.stats.copy(),
            'components': self._get_active_components(),
            'voice_status': self.voice_manager.get_status() if hasattr(self.voice_manager, 'get_status') else {},
            'tts_status': self.tts_manager.get_current_settings() if hasattr(self.tts_manager, 'get_current_settings') else {}
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history"""
        return [asdict(exec) for exec in self.execution_history[-limit:]]
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
        logger.info("Execution history cleared")

# Global orchestrator instance
_orchestrator = None

def get_orchestrator(
    config_manager: ConfigManager = None,
    event_bus: EventBus = None,
    profile_manager: ProfileManager = None
) -> SafwanBuddyOrchestrator:
    """Get or create global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        if not all([config_manager, event_bus, profile_manager]):
            raise ValueError("All components required for first orchestrator initialization")
        _orchestrator = SafwanBuddyOrchestrator(config_manager, event_bus, profile_manager)
    return _orchestrator

def process_command(text: str, source: str = "manual"):
    """Process a command using global orchestrator"""
    return get_orchestrator().process_command(text, source)

def start_orchestrator():
    """Start the global orchestrator"""
    return get_orchestrator().start()

def stop_orchestrator():
    """Stop the global orchestrator"""
    get_orchestrator().stop()