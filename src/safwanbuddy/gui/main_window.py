from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from src.safwanbuddy.gui.holographic_ui import HolographicUI
from src.safwanbuddy.gui.voice_visualizer import VoiceVisualizer
from src.safwanbuddy.core.events import event_bus

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SafwanBuddy Ultimate++ v7.0")
        self.resize(1000, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Voice Visualizer
        self.visualizer = VoiceVisualizer()
        self.layout.addWidget(self.visualizer)

        # Holographic Background
        self.holo_bg = HolographicUI()
        self.layout.addWidget(self.holo_bg, stretch=1)
        
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

    def send_command(self):
        text = self.command_input.text()
        if text:
            self.add_message(f"User: {text}")
            event_bus.emit("voice_command", text)
            self.command_input.clear()

    def add_message(self, message: str):
        self.chat_display.append(message)
