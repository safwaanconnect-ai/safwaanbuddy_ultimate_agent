from src.safwanbuddy.core.plugin_loader import PluginBase
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.utils.win_utils import WinUtils
import os
import re

class SystemOpsPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "System Operations"
        self.description = "Handles advanced system control, volume, brightness, and power"

    def activate(self):
        self.event_bus.subscribe("voice_command", self.handle_command)
        self.event_bus.subscribe("system_control", self.handle_control)

    def handle_command(self, text: str):
        text = text.lower()
        
        # Power commands
        if "lock workstation" in text or "lock pc" in text:
            logger.info("Locking workstation...")
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif "shutdown pc" in text or "turn off computer" in text:
            WinUtils.power_action("shutdown")
        elif "restart pc" in text:
            WinUtils.power_action("restart")
        elif "put pc to sleep" in text:
            WinUtils.power_action("sleep")
            
        # Volume control
        volume_match = re.search(r"set volume to (\d+) percent", text)
        if volume_match:
            level = int(volume_match.group(1)) / 100.0
            WinUtils.set_volume(level)
            logger.info(f"Volume set to {level*100}%")
        
        # Brightness control
        brightness_match = re.search(r"set brightness to (\d+) percent", text)
        if brightness_match:
            level = int(brightness_match.group(1))
            WinUtils.set_brightness(level)
            logger.info(f"Brightness set to {level}%")

        # App management
        elif "open notepad" in text:
            os.system("notepad.exe")
        elif "close notepad" in text:
            WinUtils.close_window("Notepad")

    def handle_control(self, data: dict):
        action = data.get("action")
        value = data.get("value")
        target = data.get("target")
        plan = data.get("plan")
        
        if action == "volume":
            WinUtils.set_volume(float(value or 0))
        elif action == "brightness":
            WinUtils.set_brightness(int(value or 50))
        elif action == "power":
            WinUtils.power_action(value)
        elif action == "close_window":
            WinUtils.close_window(target)
        elif action == "get_stats":
            stats = WinUtils.get_system_stats()
            logger.info(f"System Stats: {stats}")
            self.event_bus.emit("expert_event", {"status": f"System Stats: CPU {stats['cpu']}%, RAM {stats['memory']}%"})
        elif action == "set_power_plan":
            logger.info(f"Setting power plan to {plan}")
            # Mocking power plan setting as it usually requires GUIDs on Windows
            if plan == "High Performance":
                os.system("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")

    def deactivate(self):
        self.event_bus.unsubscribe("voice_command", self.handle_command)
        self.event_bus.unsubscribe("system_control", self.handle_control)
