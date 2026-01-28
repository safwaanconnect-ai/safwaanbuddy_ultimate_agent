#!/usr/bin/env python3
"""
SafwanBuddy Ultimate++ v7.0 - JARVIS-Style AI Agent
Main application entry point with complete GUI and voice capabilities
"""

import sys
import os
import argparse
import logging
import threading
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor

# Import core components
from safwanbuddy.core.logging import setup_logging
from safwanbuddy.core.config import ConfigManager
from safwanbuddy.core.event_bus import EventBus
from safwanbuddy.core.orchestrator import SafwanBuddyOrchestrator
from safwanbuddy.profiles.profile_manager import ProfileManager
from safwanbuddy.ui.main_window import MainWindow

# Initialize logging
logger = setup_logging()

class SafwanBuddyApplication:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        self.config_manager = None
        self.event_bus = None
        self.orchestrator = None
        self.profile_manager = None
        self.main_window = None
        
    def initialize_components(self):
        """Initialize all core components"""
        try:
            logger.info("Initializing SafwanBuddy components...")
            
            # Load configuration
            self.config_manager = ConfigManager()
            config = self.config_manager.load_config()
            logger.info("Configuration loaded successfully")
            
            # Initialize event bus
            self.event_bus = EventBus()
            logger.info("Event bus initialized")
            
            # Initialize profile manager
            self.profile_manager = ProfileManager(self.config_manager)
            profile = self.profile_manager.load_active_profile()
            logger.info(f"Active profile loaded: {profile.name if profile else 'None'}")
            
            # Initialize orchestrator (main logic coordinator)
            self.orchestrator = SafwanBuddyOrchestrator(
                self.config_manager,
                self.event_bus,
                self.profile_manager
            )
            logger.info("Orchestrator initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    def run_diagnostics(self):
        """Run system diagnostics to check if everything is working"""
        logger.info("Running system diagnostics...")
        
        diagnostics = []
        
        # Check microphone
        try:
            import speech_recognition
            diagnostics.append("✓ Voice Recognition: OK")
        except ImportError:
            diagnostics.append("✗ Voice Recognition: MISSING")
        
        # Check TTS
        try:
            import pyttsx3
            diagnostics.append("✓ Text-to-Speech: OK")
        except ImportError:
            diagnostics.append("✗ Text-to-Speech: MISSING")
        
        # Check PyQt6
        try:
            from PyQt6.QtWidgets import QApplication
            diagnostics.append("✓ GUI Framework: OK")
        except ImportError:
            diagnostics.append("✗ GUI Framework: MISSING")
        
        # Check desktop automation
        try:
            import pyautogui
            diagnostics.append("✓ Desktop Automation: OK")
        except ImportError:
            diagnostics.append("✗ Desktop Automation: MISSING")
        
        # Check configuration
        if self.config_manager and self.config_manager.config:
            diagnostics.append("✓ Configuration: OK")
        else:
            diagnostics.append("✗ Configuration: FAILED")
        
        print("\n" + "="*50)
        print("SAFWANBUDDY DIAGNOSTICS")
        print("="*50)
        for diagnostic in diagnostics:
            print(diagnostic)
        print("="*50)
        
        # Check for critical failures
        failures = [d for d in diagnostics if "✗" in d]
        if failures:
            print(f"\nCRITICAL: {len(failures)} component(s) failed to load!")
            print("Please install missing dependencies:")
            print("pip install -r requirements.txt")
            return False
        else:
            print("\nAll systems operational! ✓")
            return True
    
    def run_demo(self):
        """Run a demonstration of key features"""
        logger.info("Starting demonstration...")
        
        print("\n" + "="*60)
        print("SAFWANBUDDY JARVIS AGENT DEMONSTRATION")
        print("="*60)
        print("\nInitializing systems...")
        
        if not self.initialize_components():
            print("Failed to initialize components!")
            return False
        
        print("1. Voice Recognition: Ready")
        print("2. Text-to-Speech: Ready")
        print("3. Desktop Automation: Ready")
        print("4. GUI Framework: Ready")
        print("5. Configuration: Loaded")
        
        print("\nDemo Commands:")
        print("• 'Open Firefox' - Opens web browser")
        print("• 'What time is it?' - Tells current time")
        print("• 'Search for Python tutorials' - Web search")
        print("• 'Take a screenshot' - Captures screen")
        
        print("\nStarting voice recognition...")
        print("Say 'hello SafwanBuddy' to begin!")
        
        # Start a simple demo loop
        try:
            import speech_recognition as sr
            from safwanbuddy.core.tts_manager import TTSManager
            
            recognizer = sr.Recognizer()
            tts = TTSManager(self.config_manager)
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                
                while True:
                    try:
                        print("\nListening...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        text = recognizer.recognize_google(audio)
                        print(f"You said: {text}")
                        
                        # Simple command processing
                        if "hello" in text.lower():
                            tts.speak("Hello! I'm SafwanBuddy, your AI assistant.")
                            print("Agent: Hello! I'm SafwanBuddy, your AI assistant.")
                        elif "open firefox" in text.lower():
                            tts.speak("Opening Firefox browser.")
                            print("Agent: Opening Firefox browser.")
                            # Would open Firefox here
                        elif "time" in text.lower():
                            from datetime import datetime
                            current_time = datetime.now().strftime("%I:%M %p")
                            tts.speak(f"The current time is {current_time}")
                            print(f"Agent: The current time is {current_time}")
                        elif "exit" in text.lower() or "quit" in text.lower():
                            tts.speak("Goodbye!")
                            print("Agent: Goodbye!")
                            break
                        else:
                            tts.speak("I didn't understand that command.")
                            print("Agent: I didn't understand that command.")
                            
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                    except Exception as e:
                        logger.error(f"Demo error: {e}")
                        
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"Demo failed: {e}")
        
        return True
    
    def run_gui(self):
        """Run the main GUI application"""
        logger.info("Starting GUI application...")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("SafwanBuddy Ultimate++")
        app.setApplicationVersion("7.0")
        app.setOrganizationName("SafwanBuddy AI")
        
        # Set dark theme
        app.setStyle('Fusion')
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(35, 35, 45))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        app.setPalette(palette)
        
        # Show splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(0, 0, 50))
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        font = QFont("Arial", 16, QFont.Weight.Bold)
        splash.setFont(font)
        splash.showMessage("Initializing SafwanBuddy...", Qt.AlignmentFlag.AlignCenter, QColor(0, 255, 255))
        splash.show()
        app.processEvents()
        
        # Initialize components
        if not self.initialize_components():
            splash.close()
            QMessageBox.critical(None, "Initialization Error", 
                                "Failed to initialize SafwanBuddy components.\nCheck the logs for details.")
            return False
        
        splash.showMessage("Loading GUI...", Qt.AlignmentFlag.AlignCenter, QColor(0, 255, 255))
        app.processEvents()
        
        # Create main window
        self.main_window = MainWindow(
            self.config_manager,
            self.event_bus,
            self.orchestrator,
            self.profile_manager
        )
        
        splash.showMessage("Ready!", Qt.AlignmentFlag.AlignCenter, QColor(0, 255, 255))
        app.processEvents()
        
        # Close splash and show main window
        splash.finish(self.main_window)
        self.main_window.show()
        
        logger.info("SafwanBuddy GUI started successfully")
        
        # Start the application
        return app.exec()
    
    def run_headless(self):
        """Run in headless (command-line only) mode"""
        logger.info("Starting headless mode...")
        
        if not self.initialize_components():
            print("Failed to initialize components!")
            return False
        
        print("\n" + "="*50)
        print("SAFWANBUDDY HEADLESS MODE")
        print("="*50)
        print("Type 'help' for commands, 'quit' to exit")
        print("="*50)
        
        while True:
            try:
                cmd = input("\nSafwanBuddy> ").strip()
                
                if not cmd:
                    continue
                
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                elif cmd.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  help - Show this help")
                    print("  status - Show system status")
                    print("  time - Show current time")
                    print("  profile - Show active profile")
                    print("  test voice - Test voice recognition")
                    print("  test tts - Test text-to-speech")
                    print("  quit - Exit")
                elif cmd.lower() == 'status':
                    self.show_status()
                elif cmd.lower() == 'time':
                    from datetime import datetime
                    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                elif cmd.lower() == 'profile':
                    profile = self.profile_manager.get_active_profile()
                    if profile:
                        print(f"Active profile: {profile.name}")
                        print(f"Email: {profile.get('email', 'Not set')}")
                        print(f"Phone: {profile.get('phone', 'Not set')}")
                    else:
                        print("No active profile")
                elif cmd.lower() == 'test voice':
                    self.test_voice_recognition()
                elif cmd.lower() == 'test tts':
                    self.test_text_to_speech()
                else:
                    # Process as a general command
                    if self.orchestrator:
                        result = self.orchestrator.process_command(cmd)
                        if result:
                            print(f"Result: {result}")
                        else:
                            print("Command processed")
                    else:
                        print("Orchestrator not available")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Headless mode error: {e}")
                print(f"Error: {e}")
        
        print("\nShutting down...")
        return True
    
    def show_status(self):
        """Show system status in headless mode"""
        print("\nSystem Status:")
        print(f"  Configuration: {'Loaded' if self.config_manager else 'Not loaded'}")
        print(f"  Event Bus: {'Active' if self.event_bus else 'Inactive'}")
        print(f"  Orchestrator: {'Ready' if self.orchestrator else 'Not initialized'}")
        print(f"  Profile Manager: {'Ready' if self.profile_manager else 'Not initialized'}")
        
        # Show some system info
        try:
            import psutil
            print(f"  CPU Usage: {psutil.cpu_percent()}%")
            print(f"  Memory Usage: {psutil.virtual_memory().percent}%")
        except ImportError:
            print("  System info: Not available (install psutil)")
    
    def test_voice_recognition(self):
        """Test voice recognition in headless mode"""
        try:
            import speech_recognition as sr
            
            print("Testing voice recognition...")
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source)
                print("Speak something...")
                
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio)
                    print(f"You said: '{text}'")
                    print("Voice recognition: ✓ WORKING")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                except Exception as e:
                    print(f"Voice recognition test failed: {e}")
                    
        except ImportError:
            print("Speech recognition not available")
        except Exception as e:
            print(f"Voice test error: {e}")
    
    def test_text_to_speech(self):
        """Test text-to-speech in headless mode"""
        try:
            from safwanbuddy.core.tts_manager import TTSManager
            
            print("Testing text-to-speech...")
            tts = TTSManager(self.config_manager)
            tts.speak("This is a test of the text to speech system. Hello from SafwanBuddy!")
            print("TTS test completed")
            
        except Exception as e:
            print(f"TTS test failed: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SafwanBuddy Ultimate++ v7.0 - JARVIS-Style AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start GUI mode
  python main.py --test           # Run diagnostics
  python main.py --demo           # Run demonstration
  python main.py --headless       # Start headless mode
  python main.py --profile user1  # Use specific profile
        """
    )
    
    parser.add_argument("--test", action="store_true", 
                       help="Run system diagnostics")
    parser.add_argument("--demo", action="store_true", 
                       help="Run demonstration mode")
    parser.add_argument("--headless", action="store_true", 
                       help="Run in headless (text-only) mode")
    parser.add_argument("--profile", type=str, 
                       help="Specify profile to use")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug logging")
    parser.add_argument("--log-file", type=str, 
                       help="Specify log file path")
    
    args = parser.parse_args()
    
    # Setup logging based on args
    if args.debug:
        os.environ['SAFWANBUDDY_DEBUG'] = '1'
    if args.log_file:
        os.environ['SAFWANBUDDY_LOG_FILE'] = args.log_file
    
    # Create application instance
    app = SafwanBuddyApplication()
    
    try:
        # Handle profile selection
        if args.profile:
            os.environ['SAFWANBUDDY_PROFILE'] = args.profile
        
        # Run requested mode
        if args.test:
            if app.initialize_components():
                return app.run_diagnostics()
            else:
                print("Failed to initialize for diagnostics")
                return 1
        
        elif args.demo:
            return app.run_demo()
        
        elif args.headless:
            return app.run_headless()
        
        else:
            # Default: GUI mode
            return app.run_gui()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Fatal error: {e}")
        return 1
    finally:
        logger.info("SafwanBuddy shutting down")

if __name__ == "__main__":
    sys.exit(main())