"""System health and performance tracking."""

import logging
import psutil
from typing import Dict

from ..core.config import ConfigManager


class SystemMonitor:
    """Monitor system resources."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage information."""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total / (1024 ** 3),
            "available": mem.available / (1024 ** 3),
            "used": mem.used / (1024 ** 3),
            "percent": mem.percent
        }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage information."""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total / (1024 ** 3),
            "used": disk.used / (1024 ** 3),
            "free": disk.free / (1024 ** 3),
            "percent": disk.percent
        }
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information."""
        return {
            "cpu": {
                "usage": self.get_cpu_usage(),
                "count": psutil.cpu_count()
            },
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage()
        }
