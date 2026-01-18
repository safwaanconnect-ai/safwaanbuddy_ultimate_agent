import importlib
import os
import sys
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.events import event_bus

class PluginBase:
    def __init__(self):
        self.name = "Base Plugin"
        self.description = "Base class for all plugins"
        self.event_bus = event_bus

    def activate(self):
        pass

    def deactivate(self):
        pass

class PluginLoader:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = []
        if self.plugin_dir not in sys.path:
            sys.path.append(self.plugin_dir)

    def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, PluginBase) and attr is not PluginBase:
                            plugin_instance = attr()
                            plugin_instance.activate()
                            self.plugins.append(plugin_instance)
                            logger.info(f"Loaded plugin: {plugin_instance.name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {module_name}: {e}")

plugin_loader = PluginLoader()
