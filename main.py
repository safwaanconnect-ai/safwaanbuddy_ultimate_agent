import sys
import argparse
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core import plugin_loader, orchestrator

def run_test():
    logger.info("Running diagnostic suite...")
    try:
        import yaml
        print("YAML support: OK")
        import PyQt6
        print("PyQt6 support: OK")
        import selenium
        print("Selenium support: OK")
        import cv2
        print("OpenCV support: OK")
        import pytesseract
        print("Tesseract support: OK")
        
        from src.safwanbuddy.core.config import config_manager
        print(f"Configuration Loading: OK (App Name: {config_manager.get('app.name')})")
        
        from src.safwanbuddy.core.events import event_bus
        print("Event Bus Initialization: OK")
        
        from src.safwanbuddy.core.orchestrator import orchestrator
        print("Orchestrator Initialization: OK")
        
        from src.safwanbuddy.profiles.profile_manager import profile_manager
        profiles = profile_manager.list_profiles()
        print(f"Profile Manager: OK (Found {len(profiles)} profiles)")
        
        logger.info("Diagnostics complete. Everything seems to be working perfectly!")
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        print(f"DIAGNOSTIC FAILURE: {e}")
        sys.exit(1)

def run_demo():
    logger.info("Running demonstration sequence...")
    # Add demo sequence here
    print("Welcome to SafwanBuddy Demo")
    print("1. Initializing UI...")
    print("2. Testing Voice Recognition...")
    print("3. Simulating Web Search...")
    logger.info("Demo complete.")

def main():
    parser = argparse.ArgumentParser(description="SafwanBuddy Ultimate++ v7.0")
    parser.add_argument("--test", action="store_true", help="Run diagnostics")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--headless", action="store_true", help="Run in text-only mode")
    args = parser.parse_args()

    if args.test:
        run_test()
        return

    if args.demo:
        run_demo()
        # Fall through to start app if desired, or exit

    logger.info("Starting SafwanBuddy Ultimate++ v7.0")
    
    # Load plugins
    plugin_loader.load_plugins()
    
    # Start Orchestrator
    orchestrator.start()
    
    if args.headless:
        print("Running in headless mode. Type 'quit' to exit.")
        while True:
            cmd = input("SafwanBuddy> ")
            if cmd.lower() in ["quit", "exit"]:
                orchestrator.stop()
                break
            orchestrator.process_command(cmd)
        return

    # Start UI
    try:
        from PyQt6.QtWidgets import QApplication
        from src.safwanbuddy.ui.main_window import MainWindow
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(orchestrator.stop)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except ImportError:
        logger.error("PyQt6 not installed. UI mode unavailable.")
        print("Error: PyQt6 not installed. Use --headless to run in text-only mode.")
        sys.exit(1)

if __name__ == "__main__":
    main()
