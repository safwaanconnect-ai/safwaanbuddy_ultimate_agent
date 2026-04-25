import sys
import time
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.utils.win_utils import WinUtils

class WindowManager:
    def __init__(self):
        self.active_window = None

    def list_windows(self):
        return WinUtils.list_windows()

    def find_window(self, title_substring):
        windows = self.list_windows()
        for win in windows:
            if title_substring.lower() in win['title'].lower():
                return win['hwnd']
        return None

    def focus_window(self, hwnd):
        if sys.platform != 'win32': return False
        try:
            import win32gui
            import win32con
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            logger.error(f"Failed to focus window {hwnd}: {e}")
            return False

    def close_window(self, hwnd_or_title):
        if isinstance(hwnd_or_title, str):
            return WinUtils.close_window(hwnd_or_title)
        else:
            if sys.platform != 'win32': return False
            try:
                import win32gui
                import win32con
                win32gui.PostMessage(hwnd_or_title, win32con.WM_CLOSE, 0, 0)
                return True
            except Exception as e:
                logger.error(f"Failed to close window {hwnd_or_title}: {e}")
                return False

    def resize_window(self, hwnd, x, y, width, height):
        if sys.platform != 'win32': return False
        try:
            import win32gui
            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return True
        except Exception as e:
            logger.error(f"Failed to resize window {hwnd}: {e}")
            return False

    def get_system_stats(self):
        return WinUtils.get_system_stats()

window_manager = WindowManager()

# Integration with Event Bus
def handle_system_control(data):
    action = data.get("action")
    target = data.get("target")
    value = data.get("value")
    
    if action == "list_windows":
        wins = window_manager.list_windows()
        event_bus.emit("system_log", f"Found {len(wins)} active windows.")
        return wins
    
    if action == "close_window" and target:
        if window_manager.close_window(target):
            event_bus.emit("system_log", f"Closed window: {target}")
        else:
            event_bus.emit("system_log", f"Could not find window: {target}")

    if action == "focus_window" and target:
        hwnd = window_manager.find_window(target)
        if hwnd:
            window_manager.focus_window(hwnd)
            event_bus.emit("system_log", f"Focused window: {target}")

    if action == "set_volume" and value is not None:
        WinUtils.set_volume(float(value))
        event_bus.emit("system_log", f"Volume set to {value}")

    if action == "set_brightness" and value is not None:
        WinUtils.set_brightness(int(value))
        event_bus.emit("system_log", f"Brightness set to {value}")

    if action == "power_action" and target:
        WinUtils.power_action(target)
        event_bus.emit("system_log", f"Power action initiated: {target}")

    if action == "get_stats":
        stats = window_manager.get_system_stats()
        event_bus.emit("system_log", f"System Stats: {stats}")
        return stats

event_bus.subscribe("system_control", handle_system_control)
