"""Common utility functions."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp.
    
    Args:
        dt: Datetime object (current time if None)
        format_str: Format string
        
    Returns:
        Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem use.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    return filename or "unnamed"


def parse_time_duration(duration_str: str) -> int:
    """Parse time duration string to seconds.
    
    Args:
        duration_str: Duration string (e.g., "1h 30m", "45s")
        
    Returns:
        Duration in seconds
    """
    total_seconds = 0
    
    hours = re.search(r'(\d+)h', duration_str)
    if hours:
        total_seconds += int(hours.group(1)) * 3600
    
    minutes = re.search(r'(\d+)m', duration_str)
    if minutes:
        total_seconds += int(minutes.group(1)) * 60
    
    seconds = re.search(r'(\d+)s', duration_str)
    if seconds:
        total_seconds += int(seconds.group(1))
    
    return total_seconds


def ensure_path(path: Path) -> Path:
    """Ensure path exists.
    
    Args:
        path: Path to create
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
