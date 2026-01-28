#!/usr/bin/env python3
"""
Logging Configuration for SafwanBuddy
Sets up comprehensive logging for all components
"""

import logging
import logging.handlers
import sys
import os
import colorlog
from pathlib import Path
from typing import Optional
from datetime import datetime

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None,
    color_console: bool = True
) -> logging.Logger:
    """
    Set up comprehensive logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (auto-generated if None)
        console_output: Whether to output to console
        file_output: Whether to output to file
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        format_string: Custom format string for logs
        color_console: Whether to use colored console output
        
    Returns:
        logging.Logger: Configured root logger
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log file path
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"safwanbuddy_{timestamp}.log"
    
    # Configure level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    if format_string is None:
        if color_console and console_output:
            format_string = (
                "%(log_color)s%(asctime)s - %(name)s - "
                "%(levelname)s - %(message)s%(reset)s"
            )
        else:
            format_string = (
                "%(asctime)s - %(name)s - "
                "%(levelname)s - %(message)s"
            )
    
    # Set up console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        if color_console:
            console_formatter = colorlog.ColoredFormatter(
                format_string,
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'
                }
            )
        else:
            console_formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
        
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(log_level)
    
    # Set up file handler
    if file_output:
        # Use rotating file handler for better log management
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add handlers
    if console_output:
        root_logger.addHandler(console_handler)
    
    if file_output:
        root_logger.addHandler(file_handler)
    
    # Log startup information
    root_logger.info("=" * 60)
    root_logger.info("SAFWANBUDDY LOGGING SYSTEM INITIALIZED")
    root_logger.info("=" * 60)
    root_logger.info(f"Log Level: {level}")
    root_logger.info(f"Console Output: {console_output}")
    root_logger.info(f"File Output: {file_output}")
    if file_output:
        root_logger.info(f"Log File: {log_file}")
    root_logger.info(f"Max File Size: {max_file_size // (1024*1024)}MB")
    root_logger.info(f"Backup Count: {backup_count}")
    root_logger.info("=" * 60)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific component
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

def setup_component_logger(
    component_name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a dedicated logger for a specific component
    
    Args:
        component_name: Name of the component
        level: Logging level
        log_file: Optional dedicated log file for this component
        
    Returns:
        logging.Logger: Configured logger
    """
    logger_name = f"safwanbuddy.{component_name}"
    
    if log_file:
        # Create dedicated file handler for this component
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        
        logger = logging.getLogger(logger_name)
        logger.addHandler(file_handler)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.propagate = False  # Don't propagate to root logger
        
        return logger
    else:
        return get_logger(logger_name)

class PerformanceLogger:
    """Logger specifically for performance measurements"""
    
    def __init__(self, logger_name: str = "safwanbuddy.performance"):
        self.logger = get_logger(logger_name)
        self.start_times = {}
    
    def start_timer(self, operation_name: str):
        """Start timing an operation"""
        import time
        self.start_times[operation_name] = time.time()
    
    def end_timer(self, operation_name: str, additional_info: str = ""):
        """End timing and log the result"""
        import time
        
        if operation_name not in self.start_times:
            self.logger.warning(f"Timer '{operation_name}' was not started")
            return
        
        elapsed = time.time() - self.start_times[operation_name]
        
        message = f"Operation '{operation_name}' completed in {elapsed:.3f} seconds"
        if additional_info:
            message += f" - {additional_info}"
        
        self.logger.info(message)
        
        # Clean up
        del self.start_times[operation_name]
        
        return elapsed
    
    def log_memory_usage(self, component_name: str = ""):
        """Log current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_mb = memory_info.rss / (1024 * 1024)
            component = f" ({component_name})" if component_name else ""
            
            self.logger.info(f"Memory usage{component}: {memory_mb:.2f} MB")
            
        except ImportError:
            self.logger.debug("psutil not available for memory monitoring")
    
    def log_cpu_usage(self, component_name: str = ""):
        """Log current CPU usage"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            component = f" ({component_name})" if component_name else ""
            
            self.logger.info(f"CPU usage{component}: {cpu_percent:.1f}%")
            
        except ImportError:
            self.logger.debug("psutil not available for CPU monitoring")

class CommandLogger:
    """Logger for voice commands and responses"""
    
    def __init__(self):
        self.logger = get_logger("safwanbuddy.commands")
    
    def log_command(self, command: str, source: str = "voice", confidence: float = None):
        """Log a voice command"""
        confidence_str = f" (confidence: {confidence:.2f})" if confidence else ""
        self.logger.info(f"COMMAND[{source.upper()}]: '{command}'{confidence_str}")
    
    def log_response(self, response: str, duration: float = None):
        """log a voice response"""
        duration_str = f" (duration: {duration:.2f}s)" if duration else ""
        self.logger.info(f"RESPONSE: '{response}'{duration_str}")
    
    def log_intent(self, intent: str, confidence: float, parameters: dict = None):
        """Log intent recognition"""
        params_str = f" - Parameters: {parameters}" if parameters else ""
        self.logger.info(f"INTENT: '{intent}' (confidence: {confidence:.2f}){params_str}")
    
    def log_execution(self, action: str, result: str, duration: float = None):
        """Log action execution"""
        duration_str = f" (duration: {duration:.2f}s)" if duration else ""
        self.logger.info(f"EXECUTION: {action} - {result}{duration_str}")

# Initialize logging based on environment variables
def initialize_logging():
    """Initialize logging based on environment settings"""
    
    # Check for debug mode
    debug_mode = os.environ.get('SAFWANBUDDY_DEBUG', '0') == '1'
    level = "DEBUG" if debug_mode else "INFO"
    
    # Check for custom log file
    log_file = os.environ.get('SAFWANBUDDY_LOG_FILE')
    
    # Check for environment
    environment = os.environ.get('SAFWANBUDDY_ENV', 'production')
    color_output = environment != 'production'
    
    # Set up logging
    setup_logging(
        level=level,
        log_file=log_file,
        color_console=color_output
    )
    
    # Log environment info
    logger = get_logger(__name__)
    logger.info(f"Environment: {environment}")
    logger.info(f"Debug mode: {debug_mode}")

# Global logger instances
performance_logger = None
command_logger = None

def get_performance_logger() -> PerformanceLogger:
    """Get or create performance logger"""
    global performance_logger
    if performance_logger is None:
        performance_logger = PerformanceLogger()
    return performance_logger

def get_command_logger() -> CommandLogger:
    """Get or create command logger"""
    global command_logger
    if command_logger is None:
        command_logger = CommandLogger()
    return command_logger

# Auto-initialize logging
initialize_logging()

# Create main logger for the application
logger = get_logger(__name__)
logger.info("SafwanBuddy logging module loaded successfully")