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
        
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)

    def show_notification(self, text: str, duration: int = 3000):
        self.label.setText(text)
        self.show()
        self.hide_timer.start(duration)
