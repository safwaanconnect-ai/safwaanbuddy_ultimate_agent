"""Main application window with modern dark theme."""

import logging
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QLineEdit, QPushButton, QLabel,
        QTabWidget, QListWidget, QSplitter
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont, QColor, QPalette
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    logging.warning("PyQt6 not available, GUI disabled")

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


if PYQT6_AVAILABLE:
    class MainWindow(QMainWindow):
        """Main application window."""
        
        def __init__(self):
            super().__init__()
            
            self.logger = logging.getLogger(__name__)
            self.config = ConfigManager()
            self.event_bus = EventBus()
            
            self.setWindowTitle("SafwaanBuddy Ultimate++ v7.0")
            self.resize(
                self.config.get("gui.width", 1200),
                self.config.get("gui.height", 800)
            )
            
            self._setup_ui()
            self._apply_theme()
            self._connect_events()
            
            self.logger.info("Main window initialized")
        
        def _setup_ui(self) -> None:
            """Setup user interface."""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            main_layout = QVBoxLayout(central_widget)
            
            self.tabs = QTabWidget()
            main_layout.addWidget(self.tabs)
            
            self._create_chat_tab()
            self._create_automation_tab()
            self._create_browser_tab()
            self._create_dashboard_tab()
            self._create_settings_tab()
        
        def _create_chat_tab(self) -> None:
            """Create chat interface tab."""
            chat_widget = QWidget()
            layout = QVBoxLayout(chat_widget)
            
            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            self.chat_display.setPlaceholderText("Chat messages will appear here...")
            layout.addWidget(self.chat_display)
            
            input_layout = QHBoxLayout()
            
            self.chat_input = QLineEdit()
            self.chat_input.setPlaceholderText("Type your command or message...")
            self.chat_input.returnPressed.connect(self._send_message)
            input_layout.addWidget(self.chat_input)
            
            self.send_button = QPushButton("Send")
            self.send_button.clicked.connect(self._send_message)
            input_layout.addWidget(self.send_button)
            
            layout.addLayout(input_layout)
            
            self.tabs.addTab(chat_widget, "Chat")
        
        def _create_automation_tab(self) -> None:
            """Create automation control tab."""
            automation_widget = QWidget()
            layout = QVBoxLayout(automation_widget)
            
            label = QLabel("Automation Controls")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            controls_layout = QHBoxLayout()
            
            self.record_button = QPushButton("Record Workflow")
            controls_layout.addWidget(self.record_button)
            
            self.playback_button = QPushButton("Playback Workflow")
            controls_layout.addWidget(self.playback_button)
            
            self.fill_form_button = QPushButton("Fill Form")
            controls_layout.addWidget(self.fill_form_button)
            
            layout.addLayout(controls_layout)
            
            self.workflow_list = QListWidget()
            layout.addWidget(self.workflow_list)
            
            layout.addStretch()
            
            self.tabs.addTab(automation_widget, "Automation")
        
        def _create_browser_tab(self) -> None:
            """Create web browser control tab."""
            browser_widget = QWidget()
            layout = QVBoxLayout(browser_widget)
            
            url_layout = QHBoxLayout()
            
            self.url_input = QLineEdit()
            self.url_input.setPlaceholderText("Enter URL or search query...")
            url_layout.addWidget(self.url_input)
            
            self.go_button = QPushButton("Go")
            url_layout.addWidget(self.go_button)
            
            layout.addLayout(url_layout)
            
            controls_layout = QHBoxLayout()
            
            self.open_browser_button = QPushButton("Open Browser")
            controls_layout.addWidget(self.open_browser_button)
            
            self.close_browser_button = QPushButton("Close Browser")
            controls_layout.addWidget(self.close_browser_button)
            
            layout.addLayout(controls_layout)
            
            layout.addStretch()
            
            self.tabs.addTab(browser_widget, "Browser")
        
        def _create_dashboard_tab(self) -> None:
            """Create system dashboard tab."""
            dashboard_widget = QWidget()
            layout = QVBoxLayout(dashboard_widget)
            
            self.status_label = QLabel("System Status: Ready")
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.status_label)
            
            self.system_info = QTextEdit()
            self.system_info.setReadOnly(True)
            layout.addWidget(self.system_info)
            
            self.tabs.addTab(dashboard_widget, "Dashboard")
        
        def _create_settings_tab(self) -> None:
            """Create settings tab."""
            settings_widget = QWidget()
            layout = QVBoxLayout(settings_widget)
            
            label = QLabel("Settings")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            layout.addStretch()
            
            self.tabs.addTab(settings_widget, "Settings")
        
        def _apply_theme(self) -> None:
            """Apply dark theme styling."""
            theme = self.config.get("gui.theme", "dark")
            
            if theme == "dark":
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: #1e1e1e;
                    }
                    QWidget {
                        background-color: #1e1e1e;
                        color: #ffffff;
                    }
                    QTextEdit, QLineEdit {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 1px solid #00ffff;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QPushButton {
                        background-color: #00ffff;
                        color: #000000;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 15px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00cccc;
                    }
                    QPushButton:pressed {
                        background-color: #009999;
                    }
                    QLabel {
                        color: #ffffff;
                        font-size: 14px;
                    }
                    QTabWidget::pane {
                        border: 1px solid #00ffff;
                        background-color: #1e1e1e;
                    }
                    QTabBar::tab {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        padding: 8px 20px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background-color: #00ffff;
                        color: #000000;
                    }
                    QListWidget {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 1px solid #00ffff;
                        border-radius: 5px;
                    }
                """)
        
        def _connect_events(self) -> None:
            """Connect event bus handlers."""
            self.event_bus.subscribe(EventType.VOICE_COMMAND, self._on_voice_command)
            self.event_bus.subscribe(EventType.INFO_MESSAGE, self._on_info_message)
            self.event_bus.subscribe(EventType.ERROR_OCCURRED, self._on_error)
        
        def _send_message(self) -> None:
            """Send chat message."""
            message = self.chat_input.text().strip()
            
            if message:
                self.chat_display.append(f"You: {message}")
                self.chat_input.clear()
                
                self.event_bus.emit(EventType.VOICE_COMMAND, {
                    "command": message,
                    "text": message
                })
        
        def _on_voice_command(self, event) -> None:
            """Handle voice command event."""
            command = event.data.get("command", "")
            self.chat_display.append(f"Command: {command}")
        
        def _on_info_message(self, event) -> None:
            """Handle info message event."""
            message = event.data.get("message", "")
            self.chat_display.append(f"Info: {message}")
        
        def _on_error(self, event) -> None:
            """Handle error event."""
            message = event.data.get("message", "")
            self.chat_display.append(f"Error: {message}")
        
        def closeEvent(self, event) -> None:
            """Handle window close event."""
            self.event_bus.emit(EventType.SYSTEM_SHUTDOWN, {})
            event.accept()
else:
    class MainWindow:
        """Dummy MainWindow when PyQt6 not available."""
        
        def __init__(self):
            logging.error("PyQt6 not available, GUI cannot be initialized")
