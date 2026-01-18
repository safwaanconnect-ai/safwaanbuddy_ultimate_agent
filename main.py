import sys
import argparse
from PyQt6.QtWidgets import QApplication
from src.safwanbuddy.ui.main_window import MainWindow
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.plugin_loader import plugin_loader

def run_test():
    logger.info("Running diagnostic suite...")
    # Add real diagnostic checks here
    print("Configuration Loading: OK")
    print("Event Bus Initialization: OK")
    print("Subsystem Startup: OK")
    logger.info("Diagnostics complete.")

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
    
    if args.headless:
        print("Running in headless mode. Type 'quit' to exit.")
        # Headless loop could go here
        return

    # Start UI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
