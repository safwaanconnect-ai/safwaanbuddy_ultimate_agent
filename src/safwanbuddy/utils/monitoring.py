import psutil
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.events import event_bus

class SystemMonitor:
    def __init__(self):
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "running_tasks": 0
        }
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        event_bus.subscribe("task_submitted", self._on_task_submitted)
        event_bus.subscribe("task_completed", self._on_task_completed)
        event_bus.subscribe("task_failed", self._on_task_failed)

    def _on_task_submitted(self, _):
        self.stats["total_tasks"] += 1
        self.stats["running_tasks"] += 1

    def _on_task_completed(self, _):
        self.stats["completed_tasks"] += 1
        self.stats["running_tasks"] -= 1

    def _on_task_failed(self, _):
        self.stats["failed_tasks"] += 1
        self.stats["running_tasks"] -= 1

    def get_system_stats(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        res = {
            "cpu": cpu_usage,
            "ram": ram_usage,
            **self.stats
        }
        logger.debug(f"System Stats: {res}")
        return res

    def check_health(self):
        # Perform health checks on various modules
        return True

system_monitor = SystemMonitor()
