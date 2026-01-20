from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
from src.safwanbuddy.ui.holographic_ui import HolographicUI
from src.safwanbuddy.ui.voice_visualizer import VoiceVisualizer
from src.safwanbuddy.ui.overlay_manager import OverlayManager
from src.safwanbuddy.core import event_bus, logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SafwanBuddy Ultimate++ v7.0")
        self.resize(1000, 700)
        icon_path = "assets/icons/app.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Voice Visualizer
        self.visualizer = VoiceVisualizer()
        self.layout.addWidget(self.visualizer)

        # Holographic Background
        self.holo_bg = HolographicUI()
        self.layout.addWidget(self.holo_bg, stretch=1)
        
        # Overlay Manager
        self.overlay = OverlayManager()
        
        # Chat Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: rgba(20, 20, 20, 180); color: cyan; font-family: 'Courier New';")
        self.layout.addWidget(self.chat_display, stretch=2)
        
        # Input Area
        self.input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command here...")
        self.command_input.returnPressed.connect(self.send_command)
        self.input_layout.addWidget(self.command_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_command)
        self.input_layout.addWidget(self.send_btn)
        
        self.layout.addLayout(self.input_layout)
        
        # Subscribe to events
        event_bus.subscribe("voice_command", self.add_message)
        event_bus.subscribe("system_log", self.add_message)
        event_bus.subscribe("show_targets", self.overlay.show_targets)
        event_bus.subscribe("target_selected", self.handle_target_selected)
        event_bus.subscribe("system_state", self.update_system_state)
        event_bus.subscribe("task_completed", lambda res: self.add_message(f"Task complete: {res}"))
        event_bus.subscribe("task_failed", lambda err: self.add_message(f"Task failed: {err}"))
        event_bus.subscribe("notification", self.overlay.show_notification)

    def update_system_state(self, state):
        self.visualizer.set_state(state)
        self.add_message(f"System state: {state}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F12:
            logger.warning("EMERGENCY KILL SWITCH ACTIVATED!")
            self.add_message("Emergency stop triggered.")
            event_bus.emit("emergency_stop")
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            logger.info("Interrupting current workflow...")
            event_bus.emit("interrupt_workflow")
        else:
            super().keyPressEvent(event)

    def handle_target_selected(self, target):
        x, y, w, h = target
        center_x = x + w // 2
        center_y = y + h // 2
        import pyautogui
        pyautogui.click(center_x, center_y)
        self.add_message(f"Clicked target at {center_x}, {center_y}")

    def send_command(self):
        text = self.command_input.text()
        if text:
            self.add_message(f"User: {text}")
            event_bus.emit("voice_command", text)
            self.command_input.clear()

    def add_message(self, message: str):
        self.chat_display.append(message)
