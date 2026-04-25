import ctypes
import os
import platform

# Only import Win32 specific libraries if on Windows
if platform.system() == "Windows":
    import pywintypes
    import win32gui
    import win32process
    import win32con
    import win32api
    from win32com.client import Dispatch
else:
    # Mocks for non-Windows environments (like CI/CD or Linux dev)
    win32con = type('obj', (object,), {
        'SW_SHOW': 5, 
        'SW_HIDE': 0,
        'WM_CLOSE': 0x0010
    })
    win32gui = None
    win32api = None

class WinUtils:
    @staticmethod
    def get_active_window_title():
        if platform.system() != "Windows":
            return "Non-Windows Platform"
        try:
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except:
            return "Unknown"

    @staticmethod
    def list_windows():
        if platform.system() != "Windows":
            return []
        windows = []
        def enum_handler(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append({"hwnd": hwnd, "title": title})
        win32gui.EnumWindows(enum_handler, None)
        return windows

    @staticmethod
    def close_window(title_substring):
        if platform.system() != "Windows":
            return False
        windows = WinUtils.list_windows()
        for w in windows:
            if title_substring.lower() in w["title"].lower():
                win32gui.PostMessage(w["hwnd"], win32con.WM_CLOSE, 0, 0)
                return True
        return False

    @staticmethod
    def set_volume(level):
        """Level should be 0.0 to 1.0"""
        if platform.system() != "Windows":
            return
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level, None)
        except Exception as e:
            print(f"Error setting volume: {e}")

    @staticmethod
    def set_brightness(level):
        """Level should be 0 to 100"""
        if platform.system() != "Windows":
            return
        try:
            import wmi
            c = wmi.WMI(namespace='wmi')
            methods = c.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(level, 0)
        except Exception as e:
            print(f"Error setting brightness: {e}")

    @staticmethod
    def power_action(action):
        if platform.system() != "Windows":
            return
        if action == "shutdown":
            os.system("shutdown /s /t 1")
        elif action == "restart":
            os.system("shutdown /r /t 1")
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif action == "hibernate":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 1,1,0")

    @staticmethod
    def get_system_stats():
        import psutil
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        }
