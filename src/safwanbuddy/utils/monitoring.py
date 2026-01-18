import psutil
from src.safwanbuddy.core.logging import logger

class SystemMonitor:
    def get_system_stats(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        logger.debug(f"System Stats - CPU: {cpu_usage}%, RAM: {ram_usage}%")
        return {"cpu": cpu_usage, "ram": ram_usage}

    def check_health(self):
        # Perform health checks on various modules
        return True

system_monitor = SystemMonitor()
