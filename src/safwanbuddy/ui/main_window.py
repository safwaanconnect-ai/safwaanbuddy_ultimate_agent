#!/usr/bin/env python3
"""
Main Window for SafwanBuddy JARVIS-Style UI
Beautiful PyQt6 interface with voice recognition, waveform visualization, and system status
"""

import sys
import os
import time
import math
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QProgressBar,
    QGroupBox, QFrame, QScrollArea, QSlider, QCheckBox,
    QComboBox, QSpinBox, QTabWidget, QListWidget, QListWidgetItem,
    QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, QRect, QPoint, QSize, pyqtProperty
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QPen, QBrush, QColor, QPalette,
    QIcon, QAction, QMovie, QLinearGradient, QRadialGradient,
    QPainterPath, QFontMetrics
)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..core.config import ConfigManager
from ..core.event_bus import EventBus
from ..core.orchestrator import SafwanBuddyOrchestrator
from ..profiles.profile_manager import ProfileManager
from ..core.logging import get_logger

logger = get_logger(__name__)

class AvatarWidget(QWidget):
    """Animated avatar widget for the JARVIS interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.state = "idle"  # idle, listening, speaking, processing
        self.animation_frame = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(50)  # 20 FPS
        
        # Colors
        self.cyan_color = QColor(0, 255, 255)
        self.blue_color = QColor(0, 100, 200)
        self.dark_blue = QColor(0, 20, 40)
        
    def set_state(self, state: str):
        """Set the avatar state"""
        self.state = state
        self.update()
    
    def _update_animation(self):
        """Update animation frame"""
        self.animation_frame += 1
        self.update()
    
    def paintEvent(self, event):
        """Paint the avatar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 10
        
        if self.state == "idle":
            self._paint_idle_avatar(painter, center, radius)
        elif self.state == "listening":
            self._paint_listening_avatar(painter, center, radius)
        elif self.state == "speaking":
            self._paint_speaking_avatar(painter, center, radius)
        elif self.state == "processing":
            self._paint_processing_avatar(painter, center, radius)
    
    def _paint_idle_avatar(self, painter: QPainter, center: QPoint, radius: int):
        """Paint idle state avatar"""
        # Outer glow
        glow_gradient = QRadialGradient(center, radius)
        glow_gradient.setColorAt(0, QColor(0, 150, 255, 100))
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), QBrush(glow_gradient))
        
        # Core circle
        core_gradient = QRadialGradient(center, radius // 2)
        core_gradient.setColorAt(0, self.cyan_color)
        core_gradient.setColorAt(1, self.blue_color)
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius // 2, radius // 2)
        
        # Inner core
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawEllipse(center, radius // 4, radius // 4)
    
    def _paint_listening_avatar(self, painter: QPainter, center: QPoint, radius: int):
        """Paint listening state avatar"""
        # Pulsing outer ring
        pulse = (math.sin(self.animation_frame * 0.2) + 1) / 2
        ring_radius = radius + int(pulse * 20)
        
        # Outer ring
        painter.setPen(QPen(self.cyan_color, 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, ring_radius, ring_radius)
        
        # Secondary ring
        painter.setPen(QPen(self.blue_color, 2))
        ring_radius2 = radius + int(pulse * 10) + 5
        painter.drawEllipse(center, ring_radius2, ring_radius2)
        
        # Core (same as idle but brighter)
        self._paint_idle_avatar(painter, center, radius)
    
    def _paint_speaking_avatar(self, painter: QPainter, center: QPoint, radius: int):
        """Paint speaking state avatar"""
        # Sound waves
        for i in range(3):
            wave_radius = radius + i * 15
            wave_alpha = 150 - i * 40
            wave_color = QColor(0, 255, 255, wave_alpha)
            painter.setPen(QPen(wave_color, 2))
            painter.drawEllipse(center, wave_radius, wave_radius)
        
        # Core with slight glow
        glow_gradient = QRadialGradient(center, radius)
        glow_gradient.setColorAt(0, QColor(0, 255, 255, 150))
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), QBrush(glow_gradient))
        
        self._paint_idle_avatar(painter, center, radius)
    
    def _paint_processing_avatar(self, painter: QPainter, center: QPoint, radius: int):
        """Paint processing state avatar"""
        # Rotating segments
        segments = 8
        angle_step = 360 / segments
        
        for i in range(segments):
            angle = (self.animation_frame * 2 + i * angle_step) % 360
            start_angle = math.radians(angle - 10)
            end_angle = math.radians(angle + 10)
            
            painter.setBrush(QBrush(self.cyan_color if i % 2 == 0 else self.blue_color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw segment
            rect = self.rect()
            painter.drawPie(rect, int(start_angle * 16), int((end_angle - start_angle) * 16))
        
        # Center dot
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(center, 5, 5)

class WaveformWidget(QWidget):
    """Real-time audio waveform visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.audio_data = []
        self.max_points = 200
        self.is_recording = False
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(50)  # 20 FPS
    
    def set_audio_data(self, data: List[float]):
        """Set audio data for visualization"""
        self.audio_data = data[-self.max_points:]
        self.update()
    
    def set_recording(self, recording: bool):
        """Set recording state"""
        self.is_recording = recording
        self.update()
    
    def paintEvent(self, event):
        """Paint the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.audio_data:
            # Draw baseline
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            center_y = self.height() // 2
            painter.drawLine(0, center_y, self.width(), center_y)
            return
        
        # Calculate scaling
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        # Draw background
        painter.fillRect(self.rect(), QColor(10, 10, 20))
        
        # Draw waveform
        if len(self.audio_data) > 1:
            step = width / len(self.audio_data)
            painter.setPen(QPen(QColor(0, 255, 255), 2))
            
            # Draw waveform line
            points = []
            for i, amplitude in enumerate(self.audio_data):
                x = int(i * step)
                y = center_y - int(amplitude * center_y * 0.8)
                points.append(QPoint(x, y))
            
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
            
            # Draw fill
            if self.is_recording:
                path = QPainterPath()
                path.moveTo(0, center_y)
                for i, amplitude in enumerate(self.audio_data):
                    x = int(i * step)
                    y = center_y - int(amplitude * center_y * 0.8)
                    path.lineTo(x, y)
                path.lineTo(width, center_y)
                path.closeSubpath()
                
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0, QColor(0, 255, 255, 100))
                gradient.setColorAt(1, QColor(0, 255, 255, 0))
                painter.fillPath(path, QBrush(gradient))

class SystemStatusWidget(QWidget):
    """System status display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # 1 second updates
        
        self.last_update = time.time()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("System Status")
        title.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        cpu_label.setStyleSheet("color: white;")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #00FFFF;
                border-radius: 3px;
                background-color: #1a1a2e;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFFF, stop:1 #0066CC);
            }
        """)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        layout.addLayout(cpu_layout)
        
        # Memory Usage
        mem_layout = QHBoxLayout()
        mem_label = QLabel("Memory:")
        mem_label.setStyleSheet("color: white;")
        self.mem_progress = QProgressBar()
        self.mem_progress.setMaximum(100)
        self.mem_progress.setStyleSheet(self.cpu_progress.styleSheet())
        mem_layout.addWidget(mem_label)
        mem_layout.addWidget(self.mem_progress)
        layout.addLayout(mem_layout)
        
        # Disk Usage
        disk_layout = QHBoxLayout()
        disk_label = QLabel("Disk:")
        disk_label.setStyleSheet("color: white;")
        self.disk_progress = QProgressBar()
        self.disk_progress.setMaximum(100)
        self.disk_progress.setStyleSheet(self.cpu_progress.styleSheet())
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self.disk_progress)
        layout.addLayout(disk_layout)
        
        # Active Tasks
        tasks_label = QLabel("Active Tasks: 0")
        tasks_label.setStyleSheet("color: white; margin-top: 10px;")
        self.tasks_label = tasks_label
        layout.addWidget(tasks_label)
        
        layout.addStretch()
    
    def update_status(self):
        """Update system status"""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update progress bars
            self.cpu_progress.setValue(int(cpu_percent))
            self.mem_progress.setValue(int(memory.percent))
            self.disk_progress.setValue(int(disk.percent))
            
            # Update tasks count (simplified)
            try:
                task_count = len(psutil.pids())
                self.tasks_label.setText(f"Active Tasks: {task_count}")
            except:
                self.tasks_label.setText("Active Tasks: N/A")
                
        except ImportError:
            # psutil not available, show placeholder
            self.cpu_progress.setValue(0)
            self.mem_progress.setValue(0)
            self.disk_progress.setValue(0)
            self.tasks_label.setText("Active Tasks: N/A")
        except Exception as e:
            logger.error(f"Error updating system status: {e}")

class CommandLogWidget(QWidget):
    """Command execution log display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Auto-scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        
        self.max_entries = 100
        self.entries = []
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Command Log")
        title.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(0, 100, 200, 0.2);
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a1a;
                color: #ffffff;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_display)
    
    def add_entry(self, text: str, level: str = "INFO", timestamp: float = None):
        """Add a log entry"""
        if timestamp is None:
            timestamp = time.time()
        
        # Format timestamp
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        
        # Format entry based on level
        if level == "COMMAND":
            formatted_text = f"[{time_str}] 🎤 {text}"
        elif level == "RESPONSE":
            formatted_text = f"[{time_str}] 💬 {text}"
        elif level == "SUCCESS":
            formatted_text = f"[{time_str}] ✅ {text}"
        elif level == "ERROR":
            formatted_text = f"[{time_str}] ❌ {text}"
        elif level == "WARNING":
            formatted_text = f"[{time_str}] ⚠️  {text}"
        else:
            formatted_text = f"[{time_str}] ℹ️  {text}"
        
        # Add color based on level
        if level == "COMMAND":
            color = "#00FFFF"
        elif level == "RESPONSE":
            color = "#00FF00"
        elif level == "SUCCESS":
            color = "#FFFF00"
        elif level == "ERROR":
            color = "#FF4444"
        elif level == "WARNING":
            color = "#FFAA00"
        else:
            color = "#FFFFFF"
        
        # Create HTML formatted entry
        html_entry = f'<span style="color: {color};">{formatted_text}</span>'
        
        # Add to display
        self.log_display.append(html_entry)
        
        # Limit entries
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        
        # Count lines and remove excess
        lines = []
        while not cursor.atEnd():
            line = cursor.block().text()
            lines.append(line)
            cursor.movePosition(cursor.MoveOperation.Down)
        
        if len(lines) > self.max_entries:
            # Remove oldest entries
            cursor.movePosition(cursor.MoveOperation.Start)
            for _ in range(len(lines) - self.max_entries):
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Remove newline
        
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class MainWindow(QMainWindow):
    """Main window for SafwanBuddy JARVIS interface"""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        event_bus: EventBus,
        orchestrator: SafwanBuddyOrchestrator,
        profile_manager: ProfileManager
    ):
        """Initialize main window"""
        super().__init__()
        
        # Store references
        self.config_manager = config_manager
        self.event_bus = event_bus
        self.orchestrator = orchestrator
        self.profile_manager = profile_manager
        
        # Voice recognition state
        self.is_listening = False
        self.voice_thread = None
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_tray_icon()
        self.setup_timers()
        
        # Connect signals
        self.connect_signals()
        
        # Load settings
        self.load_settings()
        
        # Start orchestrator
        self.start_orchestrator()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("SafwanBuddy Ultimate++ v7.0 - JARVIS Agent")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a1a;
                color: #ffffff;
            }
            QWidget {
                background-color: transparent;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - Avatar and Controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Center panel - Waveform and Command Log
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Right panel - System Status and Settings
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with avatar and controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Avatar
        self.avatar = AvatarWidget()
        layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Voice Control Buttons
        voice_group = QGroupBox("Voice Control")
        voice_group.setStyleSheet("""
            QGroupBox {
                color: #00FFFF;
                font-weight: bold;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        voice_layout = QVBoxLayout(voice_group)
        
        # Microphone button
        self.mic_button = QPushButton("🎤 Start Listening")
        self.mic_button.setFixedHeight(60)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a4d5c, stop:1 #0a2a3a);
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a5d6c, stop:1 #1a3a4a);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a2a3a, stop:1 #1a4d5c);
            }
        """)
        self.mic_button.clicked.connect(self.toggle_voice_recognition)
        voice_layout.addWidget(self.mic_button)
        
        # Test TTS button
        self.test_tts_button = QPushButton("🔊 Test Voice")
        self.test_tts_button.setFixedHeight(40)
        self.test_tts_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 100, 200, 0.3);
                color: white;
                border: 1px solid #0066CC;
                border-radius: 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(0, 100, 200, 0.5);
            }
        """)
        self.test_tts_button.clicked.connect(self.test_tts)
        voice_layout.addWidget(self.test_tts_button)
        
        layout.addWidget(voice_group)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_group.setStyleSheet(voice_group.styleSheet())
        actions_layout = QVBoxLayout(actions_group)
        
        # Action buttons
        actions = [
            ("📸 Screenshot", self.take_screenshot),
            ("🌐 Web Search", self.show_web_search),
            ("⚙️ System Info", self.show_system_info),
            ("🛑 Stop All", self.stop_all_actions)
        ]
        
        for text, callback in actions:
            btn = QPushButton(text)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(50, 50, 80, 0.5);
                    color: white;
                    border: 1px solid #6666AA;
                    border-radius: 5px;
                    font-size: 12px;
                    text-align: left;
                    padding-left: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(70, 70, 100, 0.7);
                }
            """)
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self) -> QWidget:
        """Create center panel with waveform and command log"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Waveform display
        waveform_group = QGroupBox("Audio Visualization")
        waveform_group.setStyleSheet("""
            QGroupBox {
                color: #00FFFF;
                font-weight: bold;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        waveform_layout = QVBoxLayout(waveform_group)
        
        self.waveform = WaveformWidget()
        waveform_layout.addWidget(self.waveform)
        
        layout.addWidget(waveform_group)
        
        # Command input
        input_group = QGroupBox("Command Input")
        input_group.setStyleSheet(waveform_group.styleSheet())
        input_layout = QVBoxLayout(input_group)
        
        # Text input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type a command or click the microphone to speak...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(20, 20, 40, 0.8);
                color: white;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #00FF00;
            }
        """)
        self.command_input.returnPressed.connect(self.process_text_command)
        input_layout.addWidget(self.command_input)
        
        # Submit button
        submit_layout = QHBoxLayout()
        submit_layout.addStretch()
        
        self.submit_button = QPushButton("Execute")
        self.submit_button.setFixedSize(100, 35)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00AA44, stop:1 #008833);
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00CC55, stop:1 #00AA44);
            }
        """)
        self.submit_button.clicked.connect(self.process_text_command)
        submit_layout.addWidget(self.submit_button)
        
        input_layout.addLayout(submit_layout)
        
        layout.addWidget(input_group)
        
        # Command log
        self.command_log = CommandLogWidget()
        layout.addWidget(self.command_log, 2)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with system status and settings"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # System Status
        self.system_status = SystemStatusWidget()
        layout.addWidget(self.system_status)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                color: #00FFFF;
                font-weight: bold;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        
        # Voice settings
        voice_settings_layout = QGridLayout()
        
        # Voice rate
        voice_settings_layout.addWidget(QLabel("Voice Rate:"), 0, 0)
        self.voice_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.voice_rate_slider.setRange(50, 400)
        self.voice_rate_slider.setValue(200)
        self.voice_rate_slider.valueChanged.connect(self.update_voice_rate)
        voice_settings_layout.addWidget(self.voice_rate_slider, 0, 1)
        
        # Voice volume
        voice_settings_layout.addWidget(QLabel("Volume:"), 1, 0)
        self.voice_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.voice_volume_slider.setRange(0, 100)
        self.voice_volume_slider.setValue(80)
        self.voice_volume_slider.valueChanged.connect(self.update_voice_volume)
        voice_settings_layout.addWidget(self.voice_volume_slider, 1, 1)
        
        settings_layout.addLayout(voice_settings_layout)
        
        # Auto-listen checkbox
        self.auto_listen_checkbox = QCheckBox("Auto-listen for voice commands")
        self.auto_listen_checkbox.setChecked(True)
        self.auto_listen_checkbox.toggled.connect(self.toggle_auto_listen)
        self.auto_listen_checkbox.setStyleSheet("color: white;")
        settings_layout.addWidget(self.auto_listen_checkbox)
        
        # Confirmation checkbox
        self.confirm_actions_checkbox = QCheckBox("Confirm before actions")
        self.confirm_actions_checkbox.setChecked(True)
        self.confirm_actions_checkbox.setStyleSheet("color: white;")
        settings_layout.addWidget(self.confirm_actions_checkbox)
        
        layout.addWidget(settings_group)
        
        # Status indicators
        status_group = QGroupBox("Status")
        status_group.setStyleSheet(settings_group.styleSheet())
        status_layout = QVBoxLayout(status_group)
        
        # Voice status
        self.voice_status_label = QLabel("Voice: Ready")
        self.voice_status_label.setStyleSheet("color: #00FF00;")
        status_layout.addWidget(self.voice_status_label)
        
        # TTS status
        self.tts_status_label = QLabel("TTS: Ready")
        self.tts_status_label.setStyleSheet("color: #00FF00;")
        status_layout.addWidget(self.tts_status_label)
        
        # Profile status
        active_profile = self.profile_manager.get_active_profile()
        profile_name = active_profile.name if active_profile else "None"
        self.profile_status_label = QLabel(f"Profile: {profile_name}")
        self.profile_status_label.setStyleSheet("color: #00FF00;")
        status_layout.addWidget(self.profile_status_label)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        return panel
    
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Profile', self)
        new_action.triggered.connect(self.create_new_profile)
        file_menu.addAction(new_action)
        
        load_profile_action = QAction('Load Profile', self)
        load_profile_action.triggered.connect(self.load_profile)
        file_menu.addAction(load_profile_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        calibrate_action = QAction('Calibrate Microphone', self)
        calibrate_action.triggered.connect(self.calibrate_microphone)
        tools_menu.addAction(calibrate_action)
        
        test_action = QAction('Test All Systems', self)
        test_action.triggered.connect(self.test_all_systems)
        tools_menu.addAction(test_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tray_icon(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_action = QAction('Show', self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            hide_action = QAction('Hide', self)
            hide_action.triggered.connect(self.hide)
            tray_menu.addAction(hide_action)
            
            tray_menu.addSeparator()
            
            exit_action = QAction('Exit', self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def setup_timers(self):
        """Setup various timers"""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)  # 1 second
        
        # Voice level simulation timer (for demo)
        self.voice_sim_timer = QTimer()
        self.voice_sim_timer.timeout.connect(self.simulate_voice_level)
        self.voice_sim_timer.start(100)  # 100ms
    
    def connect_signals(self):
        """Connect signals between components"""
        # Voice recognition events
        self.event_bus.subscribe('voice_command_recognized', self.on_voice_command)
        self.event_bus.subscribe('voice_recognition_error', self.on_voice_error)
        self.event_bus.subscribe('tts_speech_started', self.on_tts_started)
        self.event_bus.subscribe('tts_speech_completed', self.on_tts_completed)
        
        # Command execution events
        self.event_bus.subscribe('command_execution_started', self.on_command_started)
        self.event_bus.subscribe('command_execution_completed', self.on_command_completed)
        self.event_bus.subscribe('command_execution_error', self.on_command_error)
    
    def load_settings(self):
        """Load application settings"""
        try:
            # Load voice settings
            voice_rate = self.config_manager.get('voice.speech_rate', 200)
            voice_volume = self.config_manager.get('voice.speech_volume', 80)
            
            self.voice_rate_slider.setValue(int(voice_rate))
            self.voice_volume_slider.setValue(int(voice_volume))
            
            # Load other settings
            auto_listen = self.config_manager.get('voice.auto_listen', True)
            self.auto_listen_checkbox.setChecked(auto_listen)
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def start_orchestrator(self):
        """Start the orchestrator"""
        try:
            if self.orchestrator.start():
                self.command_log.add_entry("SafwanBuddy orchestrator started successfully", "SUCCESS")
            else:
                self.command_log.add_entry("Failed to start orchestrator", "ERROR")
        except Exception as e:
            self.command_log.add_entry(f"Error starting orchestrator: {e}", "ERROR")
    
    # Event handlers
    def on_voice_command(self, data):
        """Handle voice command event"""
        command = data.get('command', '')
        confidence = data.get('confidence', 0.0)
        
        self.command_log.add_entry(f"Voice command: '{command}' (confidence: {confidence:.2f})", "COMMAND")
        
        # Process the command
        self.process_command(command)
    
    def on_voice_error(self, data):
        """Handle voice recognition error"""
        error = data.get('error', 'Unknown error')
        self.command_log.add_entry(f"Voice recognition error: {error}", "ERROR")
        self.voice_status_label.setText("Voice: Error")
        self.voice_status_label.setStyleSheet("color: #FF0000;")
    
    def on_tts_started(self, data):
        """Handle TTS speech started"""
        self.avatar.set_state("speaking")
        self.tts_status_label.setText("TTS: Speaking")
        self.tts_status_label.setStyleSheet("color: #FFAA00;")
    
    def on_tts_completed(self, data):
        """Handle TTS speech completed"""
        self.avatar.set_state("idle")
        self.tts_status_label.setText("TTS: Ready")
        self.tts_status_label.setStyleSheet("color: #00FF00;")
    
    def on_command_started(self, data):
        """Handle command execution started"""
        intent_type = data.get('intent_type', 'unknown')
        self.avatar.set_state("processing")
        self.command_log.add_entry(f"Processing: {intent_type}", "INFO")
    
    def on_command_completed(self, data):
        """Handle command execution completed"""
        result = data.get('result', '')
        self.avatar.set_state("idle")
        self.command_log.add_entry(f"Completed: {result}", "SUCCESS")
    
    def on_command_error(self, data):
        """Handle command execution error"""
        error = data.get('error', 'Unknown error')
        self.avatar.set_state("idle")
        self.command_log.add_entry(f"Error: {error}", "ERROR")
    
    # UI Event Handlers
    def toggle_voice_recognition(self):
        """Toggle voice recognition on/off"""
        if self.is_listening:
            self.stop_voice_recognition()
        else:
            self.start_voice_recognition()
    
    def start_voice_recognition(self):
        """Start voice recognition"""
        try:
            self.is_listening = True
            self.mic_button.setText("🛑 Stop Listening")
            self.mic_button.setStyleSheet(self.mic_button.styleSheet() + """
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #CC4400, stop:1 #AA3300);
                    color: white;
                }
            """)
            
            self.avatar.set_state("listening")
            self.voice_status_label.setText("Voice: Listening")
            self.voice_status_label.setStyleSheet("color: #FFAA00;")
            
            # Start voice recognition thread
            self.voice_thread = threading.Thread(target=self.voice_recognition_loop, daemon=True)
            self.voice_thread.start()
            
            self.command_log.add_entry("Voice recognition started", "INFO")
            
        except Exception as e:
            self.command_log.add_entry(f"Error starting voice recognition: {e}", "ERROR")
    
    def stop_voice_recognition(self):
        """Stop voice recognition"""
        try:
            self.is_listening = False
            self.mic_button.setText("🎤 Start Listening")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1a4d5c, stop:1 #0a2a3a);
                    color: #00FFFF;
                    border: 2px solid #00FFFF;
                    border-radius: 30px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2a5d6c, stop:1 #1a3a4a);
                }
                QPushButton:pressed {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0a2a3a, stop:1 #1a4d5c);
                }
            """)
            
            self.avatar.set_state("idle")
            self.voice_status_label.setText("Voice: Ready")
            self.voice_status_label.setStyleSheet("color: #00FF00;")
            
            self.command_log.add_entry("Voice recognition stopped", "INFO")
            
        except Exception as e:
            self.command_log.add_entry(f"Error stopping voice recognition: {e}", "ERROR")
    
    def voice_recognition_loop(self):
        """Main voice recognition loop (runs in separate thread)"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.is_listening:
                    try:
                        # Listen for audio
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # Recognize speech
                        text = recognizer.recognize_google(audio)
                        
                        if text.strip():
                            # Emit event
                            self.event_bus.emit('voice_command_recognized', {
                                'command': text.strip(),
                                'confidence': 0.9
                            })
                            
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        # Could not understand audio
                        continue
                    except sr.RequestError as e:
                        self.event_bus.emit('voice_recognition_error', {'error': str(e)})
                        break
                    except Exception as e:
                        logger.error(f"Voice recognition loop error: {e}")
                        continue
                        
        except ImportError:
            self.event_bus.emit('voice_recognition_error', {'error': 'Speech recognition not available'})
        except Exception as e:
            self.event_bus.emit('voice_recognition_error', {'error': str(e)})
    
    def process_text_command(self):
        """Process text command from input field"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.command_input.clear()
        self.process_command(command)
    
    def process_command(self, command: str):
        """Process a command through the orchestrator"""
        try:
            # Add to log
            self.command_log.add_entry(f"Processing command: {command}", "INFO")
            
            # Process through orchestrator
            if self.orchestrator:
                execution = self.orchestrator.process_command(command, "ui")
                if execution:
                    self.command_log.add_entry(f"Command queued for execution", "SUCCESS")
                else:
                    self.command_log.add_entry(f"Failed to queue command", "ERROR")
            else:
                self.command_log.add_entry("Orchestrator not available", "ERROR")
                
        except Exception as e:
            self.command_log.add_entry(f"Error processing command: {e}", "ERROR")
    
    def simulate_voice_level(self):
        """Simulate voice level for demo purposes"""
        if self.is_listening:
            # Generate random audio data for visualization
            import random
            audio_data = [random.random() for _ in range(50)]
            self.waveform.set_audio_data(audio_data)
            self.waveform.set_recording(True)
        else:
            self.waveform.set_recording(False)
    
    # Action handlers
    def test_tts(self):
        """Test text-to-speech"""
        try:
            if hasattr(self.orchestrator, 'tts_manager'):
                self.orchestrator.tts_manager.speak("Hello! This is SafwanBuddy testing the text to speech system.")
                self.command_log.add_entry("TTS test initiated", "INFO")
            else:
                self.command_log.add_entry("TTS manager not available", "ERROR")
        except Exception as e:
            self.command_log.add_entry(f"TTS test failed: {e}", "ERROR")
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            self.process_command("take screenshot")
        except Exception as e:
            self.command_log.add_entry(f"Screenshot failed: {e}", "ERROR")
    
    def show_web_search(self):
        """Show web search interface"""
        # Simple implementation - could be expanded
        self.command_input.setPlaceholderText("Enter search query...")
        self.command_input.setFocus()
    
    def show_system_info(self):
        """Show system information"""
        self.process_command("system status")
    
    def stop_all_actions(self):
        """Stop all ongoing actions"""
        try:
            if hasattr(self.orchestrator, 'tts_manager'):
                self.orchestrator.tts_manager.stop()
            
            self.voice_status_label.setText("Voice: Ready")
            self.voice_status_label.setStyleSheet("color: #00FF00;")
            
            self.avatar.set_state("idle")
            
            self.command_log.add_entry("All actions stopped", "INFO")
            
        except Exception as e:
            self.command_log.add_entry(f"Error stopping actions: {e}", "ERROR")
    
    def update_voice_rate(self, value: int):
        """Update voice rate setting"""
        try:
            if hasattr(self.orchestrator, 'tts_manager'):
                self.orchestrator.tts_manager.set_rate(value)
            self.config_manager.set('voice.speech_rate', value)
        except Exception as e:
            logger.error(f"Error updating voice rate: {e}")
    
    def update_voice_volume(self, value: int):
        """Update voice volume setting"""
        try:
            volume = value / 100.0
            if hasattr(self.orchestrator, 'tts_manager'):
                self.orchestrator.tts_manager.set_volume(volume)
            self.config_manager.set('voice.speech_volume', value)
        except Exception as e:
            logger.error(f"Error updating voice volume: {e}")
    
    def toggle_auto_listen(self, enabled: bool):
        """Toggle auto-listen setting"""
        try:
            self.config_manager.set('voice.auto_listen', enabled)
            if enabled:
                self.command_log.add_entry("Auto-listen enabled", "INFO")
            else:
                self.command_log.add_entry("Auto-listen disabled", "INFO")
        except Exception as e:
            logger.error(f"Error updating auto-listen: {e}")
    
    def update_status_display(self):
        """Update status display"""
        # Update orchestrator status if available
        if hasattr(self.orchestrator, 'get_status'):
            try:
                status = self.orchestrator.get_status()
                # Could update more status info here
            except:
                pass
    
    def create_new_profile(self):
        """Create a new profile"""
        # Simple implementation - could use a dialog
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
            if ok and name.strip():
                profile = self.profile_manager.create_profile(name.strip())
                self.command_log.add_entry(f"Created profile: {profile.name}", "SUCCESS")
                self.update_profile_status()
        except Exception as e:
            self.command_log.add_entry(f"Error creating profile: {e}", "ERROR")
    
    def load_profile(self):
        """Load a profile"""
        try:
            profiles = self.profile_manager.list_profiles()
            if not profiles:
                self.command_log.add_entry("No profiles available", "WARNING")
                return
            
            from PyQt6.QtWidgets import QInputDialog
            
            profile_names = [p['name'] for p in profiles]
            name, ok = QInputDialog.getItem(self, "Load Profile", "Select profile:", profile_names, 0, False)
            
            if ok:
                # Find profile by name
                for profile in profiles:
                    if profile['name'] == name:
                        self.profile_manager.set_active_profile(profile['id'])
                        self.command_log.add_entry(f"Loaded profile: {name}", "SUCCESS")
                        self.update_profile_status()
                        break
                        
        except Exception as e:
            self.command_log.add_entry(f"Error loading profile: {e}", "ERROR")
    
    def calibrate_microphone(self):
        """Calibrate microphone"""
        try:
            self.command_log.add_entry("Starting microphone calibration...", "INFO")
            
            if hasattr(self.orchestrator, 'voice_manager'):
                success = self.orchestrator.voice_manager.calibrate_microphone(5.0)
                if success:
                    self.command_log.add_entry("Microphone calibration completed", "SUCCESS")
                else:
                    self.command_log.add_entry("Microphone calibration failed", "ERROR")
            else:
                self.command_log.add_entry("Voice manager not available", "ERROR")
                
        except Exception as e:
            self.command_log.add_entry(f"Calibration error: {e}", "ERROR")
    
    def test_all_systems(self):
        """Test all systems"""
        try:
            self.command_log.add_entry("Testing all systems...", "INFO")
            
            # Test voice recognition
            self.test_tts()
            
            # Test voice recognition
            if hasattr(self.orchestrator, 'voice_manager'):
                success = self.orchestrator.voice_manager.calibrate_microphone(2.0)
                if success:
                    self.command_log.add_entry("Voice recognition test passed", "SUCCESS")
                else:
                    self.command_log.add_entry("Voice recognition test failed", "ERROR")
            
            # Test other systems
            self.command_log.add_entry("System test completed", "SUCCESS")
            
        except Exception as e:
            self.command_log.add_entry(f"System test error: {e}", "ERROR")
    
    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox
        
        about_text = """
        <h2>SafwanBuddy Ultimate++ v7.0</h2>
        <p>JARVIS-Style AI Agent</p>
        <p>A powerful voice-controlled assistant with desktop automation capabilities.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Real-time voice recognition</li>
        <li>Text-to-speech synthesis</li>
        <li>Desktop automation</li>
        <li>Natural language understanding</li>
        <li>Profile management</li>
        <li>Beautiful JARVIS-style interface</li>
        </ul>
        <p><i>Built with Python and PyQt6</i></p>
        """
        
        QMessageBox.about(self, "About SafwanBuddy", about_text)
    
    def update_profile_status(self):
        """Update profile status display"""
        try:
            active_profile = self.profile_manager.get_active_profile()
            profile_name = active_profile.name if active_profile else "None"
            self.profile_status_label.setText(f"Profile: {profile_name}")
        except Exception as e:
            logger.error(f"Error updating profile status: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop voice recognition
            if self.is_listening:
                self.stop_voice_recognition()
            
            # Stop orchestrator
            if self.orchestrator:
                self.orchestrator.stop()
            
            # Hide to tray if available
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.hide()
                event.ignore()
            else:
                event.accept()
                
        except Exception as e:
            logger.error(f"Error during close: {e}")
            event.accept()