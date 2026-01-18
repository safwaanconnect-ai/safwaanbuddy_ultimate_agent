from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

class OverlayManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.TransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.label = QLabel("SafwanBuddy Active")
        self.label.setStyleSheet("color: lime; font-weight: bold; font-size: 18px;")
        self.layout.addWidget(self.label)
        
        self.targets = []
        self.current_index = -1
        
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)

    def show_notification(self, text: str, duration: int = 3000):
        self.label.setText(text)
        self.show()
        self.hide_timer.start(duration)

    def show_targets(self, targets):
        """targets is a list of (x, y, w, h)"""
        self.targets = targets
        self.current_index = 0
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.TransparentForInput) # Enable input
        self.showFullScreen()
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QPen, QColor
        painter = QPainter(self)
        for i, (x, y, w, h) in enumerate(self.targets):
            if i == self.current_index:
                pen = QPen(QColor(0, 255, 255), 3) # Glowing cyan
            else:
                pen = QPen(QColor(255, 255, 0), 1) # Yellow
            painter.setPen(pen)
            painter.drawRect(x, y, w, h)
            painter.drawText(x, y - 5, str(i + 1))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            self.current_index = (self.current_index + 1) % len(self.targets)
            self.update()
        elif event.key() == Qt.Key.Key_Space:
            if 0 <= self.current_index < len(self.targets):
                target = self.targets[self.current_index]
                from src.safwanbuddy.core.events import event_bus
                event_bus.emit("target_selected", target)
                self.hide()
        elif event.key() == Qt.Key.Key_Escape:
            self.hide()
