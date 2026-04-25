from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
import random
from src.safwanbuddy.core import event_bus

class VoiceVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.bars = [0] * 50
        self.timer = QTimer()
        self.timer.timeout.connect(self.decay_bars)
        self.timer.start(50)
        self.state = "idle"  # idle, listening, processing, error
        event_bus.subscribe("audio_level", self.on_audio_level)

    def on_audio_level(self, level):
        # Update bars based on audio level
        # Spread the energy across bars
        for i in range(len(self.bars)):
            target = level * 100 * (1.0 - abs(i - 25) / 25.0) # Central hump
            self.bars[i] = max(self.bars[i], int(target + random.randint(-5, 5)))
        self.update()

    def decay_bars(self):
        if self.state != "listening":
            self.bars = [max(0, b - 10) for b in self.bars]
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
        
        base_color = QColor(0, 212, 255) # Cyan
        if self.state == "listening":
            base_color = QColor(0, 255, 136) # Neon Green
        elif self.state == "processing":
            base_color = QColor(255, 0, 85) # Vivid Pink
        elif self.state == "error":
            base_color = QColor(255, 30, 0) # Red
            
        for i, val in enumerate(self.bars):
            bar_height = (val / 100) * height
            x = int(i * bar_width)
            y = int((height - bar_height) / 2)
            
            # Create a gradient for each bar
            from PyQt6.QtGui import QLinearGradient
            gradient = QLinearGradient(0, y, 0, y + bar_height)
            gradient.setColorAt(0.0, base_color.lighter(150))
            gradient.setColorAt(0.5, base_color)
            gradient.setColorAt(1.0, base_color.darker(150))
            
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, int(bar_width - 2), int(bar_height), 2, 2)
