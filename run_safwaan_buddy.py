import sys
from PyQt6.QtWidgets import QApplication
from src.safwanbuddy.gui.main_window import MainWindow
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.plugin_loader import plugin_loader

def main():
    logger.info("Starting SafwanBuddy Ultimate++ v7.0")
    
    # Load plugins
    plugin_loader.load_plugins()
    
    # Start UI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
