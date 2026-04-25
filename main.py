import sys
import argparse
from PyQt6.QtWidgets import QApplication
from src.safwanbuddy.ui.main_window import MainWindow
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core import plugin_loader, orchestrator

def run_test():
    logger.info("Running diagnostic suite...")
    import os
    import importlib
    
    modules = [
        "src.safwanbuddy.core.orchestrator",
        "src.safwanbuddy.voice.speech_recognition",
        "src.safwanbuddy.ui.holographic_ui",
        "src.safwanbuddy.ui.sound_manager",
        "src.safwanbuddy.automation.click_system",
        "src.safwanbuddy.automation.expert_mode",
        "src.safwanbuddy.web.browser_controller"
    ]
    
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"Module {mod}: LOADED")
        except Exception as e:
            print(f"Module {mod}: FAILED ({e})")

    paths = [
        "assets/shaders/hologram.frag",
        "assets/shaders/particles.frag",
        "assets/shaders/energy_ring.frag",
        "assets/shaders/energy_orb.frag",
        "assets/sounds/startup.wav",
        "assets/sounds/success.wav",
        "assets/models/vosk-model-small-en-us-0.15"
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"Asset {path}: FOUND")
        else:
            print(f"Asset {path}: MISSING")

    logger.info("Diagnostics complete.")

def run_demo():
    logger.info("Running demonstration sequence...")
    print("Welcome to SafwanBuddy Demo")
    from src.safwanbuddy.core.events import event_bus
    import time

    print("1. Initializing UI...")
    event_bus.emit("system_state", "idle")
    time.sleep(1)
    
    print("2. Simulating Voice Recognition...")
    event_bus.emit("system_state", "listening")
    event_bus.emit("audio_level", 0.5)
    time.sleep(1)
    event_bus.emit("voice_command", "hey safwan search for top AI trends")
    
    print("3. Processing Command...")
    event_bus.emit("system_state", "processing")
    time.sleep(1)
    
    print("4. Executing Automation...")
    event_bus.emit("system_log", "Opening browser and searching...")
    time.sleep(1)
    
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
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(orchestrator.stop)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
