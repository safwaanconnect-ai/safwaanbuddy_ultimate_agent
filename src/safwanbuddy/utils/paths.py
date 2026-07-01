import os
import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_asset_path(asset_name):
    return get_resource_path(os.path.join("assets", asset_name))

def get_config_path(config_name):
    return get_resource_path(os.path.join("config", config_name))
