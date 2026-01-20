from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
import random

class VoiceVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.bars = [0] * 50
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bars)
        self.timer.start(50)
        self.state = "idle"  # idle, listening, processing, error

    def update_bars(self):
        if self.state == "listening":
            self.bars = [random.randint(10, 90) for _ in range(50)]
        elif self.state == "processing":
            self.bars = [random.randint(40, 60) for _ in range(50)]
        else:
            self.bars = [max(0, b - 5) for b in self.bars]
        self.update()

    def set_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        bar_width = width / len(self.bars)
        
        color = QColor(0, 255, 255) # Default Cyan
        if self.state == "listening":
            color = QColor(0, 255, 0) # Green
        elif self.state == "processing":
            color = QColor(255, 255, 0) # Yellow
        elif self.state == "error":
            color = QColor(255, 0, 0) # Red
            
        for i, val in enumerate(self.bars):
            bar_height = (val / 100) * height
            painter.fillRect(int(i * bar_width), int((height - bar_height) / 2), int(bar_width - 1), int(bar_height), color)
