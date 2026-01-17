"""Main application entry point."""

import sys
import logging
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

from .core.events import EventBus, EventType
from .core.config import ConfigManager
from .core.logger import setup_logger
from .voice.speech_recognition import SpeechRecognizer
from .voice.text_to_speech import TextToSpeech
from .voice.command_processor import CommandProcessor
from .gui.main_window import MainWindow
from .automation.click_system import ClickSystem
from .automation.type_system import TypeSystem
from .automation.form_filler import FormFiller
from .automation.workflow_engine import WorkflowEngine
from .web.browser_controller import BrowserController
from .web.search_engine import SearchEngine
from .profiles.profile_manager import ProfileManager
from .plugins.plugin_loader import PluginLoader
from .utils.monitoring import SystemMonitor
from .utils.alerts import AlertSystem


class SafwaanBuddyApp:
    """Main application class."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = setup_logger(
            level=logging.INFO if not self.config.get("app.debug") else logging.DEBUG
        )
        self.event_bus = EventBus()
        
        self.logger.info("=" * 60)
        self.logger.info("SafwaanBuddy Ultimate++ v7.0 Starting...")
        self.logger.info("=" * 60)
        
        self.config.load_config()
        
        self.speech_recognizer: SpeechRecognizer = None
        self.tts: TextToSpeech = None
        self.command_processor: CommandProcessor = None
        self.main_window: MainWindow = None
        self.click_system: ClickSystem = None
        self.type_system: TypeSystem = None
        self.form_filler: FormFiller = None
        self.workflow_engine: WorkflowEngine = None
        self.browser_controller: BrowserController = None
        self.search_engine: SearchEngine = None
        self.profile_manager: ProfileManager = None
        self.plugin_loader: PluginLoader = None
        self.system_monitor: SystemMonitor = None
        self.alert_system: AlertSystem = None
        
        self.qt_app = None
    
    def initialize(self) -> bool:
        """Initialize all components.
        
        Returns:
            True if successful
        """
        try:
            self.logger.info("Initializing components...")
            
            self.command_processor = CommandProcessor()
            
            if self.config.get("voice.enabled"):
                self.speech_recognizer = SpeechRecognizer()
                self.tts = TextToSpeech()
                self.logger.info("Voice subsystem initialized")
            
            self.click_system = ClickSystem()
            self.type_system = TypeSystem()
            self.form_filler = FormFiller()
            self.workflow_engine = WorkflowEngine()
            self.logger.info("Automation engine initialized")
            
            self.browser_controller = BrowserController()
            self.search_engine = SearchEngine()
            self.logger.info("Web automation initialized")
            
            self.profile_manager = ProfileManager()
            self.logger.info("Profile manager initialized")
            
            self.plugin_loader = PluginLoader()
            self.plugin_loader.load_plugins()
            self.logger.info("Plugins loaded")
            
            self.system_monitor = SystemMonitor()
            self.alert_system = AlertSystem()
            self.logger.info("Monitoring systems initialized")
            
            self._register_command_handlers()
            
            self.event_bus.emit(EventType.SYSTEM_STARTED, {})
            
            self.logger.info("All components initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def _register_command_handlers(self) -> None:
        """Register command handlers."""
        from .voice.command_processor import Command
        
        def handle_search(text, groups):
            query = groups[0] if groups else text
            self.logger.info(f"Searching for: {query}")
            if self.search_engine:
                self.search_engine.search(query)
            if self.tts:
                self.tts.speak(f"Searching for {query}")
        
        def handle_open_browser(text, groups):
            self.logger.info("Opening browser")
            if self.browser_controller:
                self.browser_controller.start_browser()
            if self.tts:
                self.tts.speak("Opening browser")
        
        def handle_help(text, groups):
            help_text = self.command_processor.get_help_text()
            self.logger.info(help_text)
            if self.tts:
                self.tts.speak("Here are the available commands")
        
        for cmd in self.command_processor.commands:
            if cmd.name == "search":
                cmd.handler = handle_search
            elif cmd.name == "open_browser":
                cmd.handler = handle_open_browser
            elif cmd.name == "help":
                cmd.handler = handle_help
    
    def start_gui(self) -> None:
        """Start GUI application."""
        if not PYQT6_AVAILABLE:
            self.logger.error("PyQt6 not available, cannot start GUI")
            return
        
        self.qt_app = QApplication(sys.argv)
        self.main_window = MainWindow()
        self.main_window.show()
        
        self.logger.info("GUI started")
        
        sys.exit(self.qt_app.exec())
    
    def start_voice(self) -> None:
        """Start voice recognition."""
        if self.speech_recognizer and self.config.get("voice.enabled"):
            self.speech_recognizer.start_listening()
            self.logger.info("Voice recognition started")
            
            if self.tts:
                self.tts.speak("SafwaanBuddy is ready. Say hey safwan to activate.")
    
    def run(self) -> None:
        """Run the application."""
        if not self.initialize():
            self.logger.error("Failed to initialize application")
            return
        
        self.start_voice()
        
        self.start_gui()
    
    def shutdown(self) -> None:
        """Shutdown application."""
        self.logger.info("Shutting down SafwaanBuddy...")
        
        if self.speech_recognizer:
            self.speech_recognizer.stop_listening()
        
        if self.browser_controller:
            self.browser_controller.close_browser()
        
        if self.plugin_loader:
            for plugin in self.plugin_loader.plugins.values():
                plugin.cleanup()
        
        self.config.save_config()
        
        self.event_bus.emit(EventType.SYSTEM_SHUTDOWN, {})
        self.logger.info("Shutdown complete")


def main():
    """Main entry point."""
    app = SafwaanBuddyApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
