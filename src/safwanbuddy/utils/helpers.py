import time
import random
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

def human_delay(min_delay=0.1, max_delay=0.5):
    """Adds a randomized delay to simulate human interaction."""
    time.sleep(random.uniform(min_delay, max_delay))

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from a filename."""
    return "".join([c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
