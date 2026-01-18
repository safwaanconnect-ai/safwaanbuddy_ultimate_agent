import mss
import numpy as np
from PIL import Image

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self, monitor_id: int = 1):
        # monitor 1 is usually the full screen
        monitor = self.sct.monitors[monitor_id]
        screenshot = self.sct.grab(monitor)
        
        # Convert to numpy array for OpenCV/other processing
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return np.array(img)

screen_capture = ScreenCapture()
