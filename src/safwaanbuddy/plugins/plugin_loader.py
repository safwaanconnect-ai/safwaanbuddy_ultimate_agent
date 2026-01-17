"""Dynamic plugin loading system."""

import logging
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class PluginBase(ABC):
    """Base class for plugins."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.event_bus = EventBus()
        self.config = ConfigManager()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin."""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality."""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass


class PluginLoader:
    """Load and manage plugins."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.plugins_dir = Path(self.config.get("plugins.dir", "src/safwaanbuddy/plugins"))
        self.plugins: Dict[str, PluginBase] = {}
    
    def load_plugins(self) -> None:
        """Load all plugins from directory."""
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
        
        for plugin_file in self.plugins_dir.glob("plugin_*.py"):
            self._load_plugin(plugin_file)
    
    def _load_plugin(self, filepath: Path) -> Optional[PluginBase]:
        """Load single plugin."""
        try:
            module_name = f"safwaanbuddy.plugins.{filepath.stem}"
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin = obj()
                    if plugin.initialize():
                        self.plugins[plugin.name] = plugin
                        self.event_bus.emit(EventType.PLUGIN_LOADED, {"name": plugin.name})
                        self.logger.info(f"Loaded plugin: {plugin.name}")
                        return plugin
        except Exception as e:
            self.logger.error(f"Failed to load plugin {filepath}: {e}")
        
        return None
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get plugin by name."""
        return self.plugins.get(name)
    
    def execute_plugin(self, name: str, *args, **kwargs) -> Any:
        """Execute plugin."""
        plugin = self.get_plugin(name)
        
        if plugin:
            try:
                result = plugin.execute(*args, **kwargs)
                self.event_bus.emit(EventType.PLUGIN_EXECUTED, {"name": name})
                return result
            except Exception as e:
                self.logger.error(f"Plugin execution failed: {e}")
                return None
        
        return None
