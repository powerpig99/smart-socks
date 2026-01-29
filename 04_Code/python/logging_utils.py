#!/usr/bin/env python3
"""
Smart Socks - Logging Utilities
ELEC-E7840 Smart Wearables (Aalto University)

Standardized logging configuration for all modules.

Usage:
    from logging_utils import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application started")
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import os

from config import LOGGING


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console: Optional[bool] = None,
    file_output: Optional[bool] = None
) -> logging.Logger:
    """
    Setup standardized logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console: Whether to output to console
        file_output: Whether to output to file
    
    Returns:
        Root logger instance
    """
    # Use config defaults if not specified
    level = level or LOGGING['level']
    log_file = log_file or LOGGING['file']
    console = console if console is not None else LOGGING['console']
    file_output = file_output if file_output is not None else LOGGING['file_output']
    
    # Convert level string to constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(
        LOGGING['format'],
        datefmt=LOGGING['date_format']
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if file_output and log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class ProgressLogger:
    """
    Simple progress logger for long-running operations.
    """
    
    def __init__(self, logger: logging.Logger, total: int, description: str = "Processing"):
        self.logger = logger
        self.total = total
        self.description = description
        self.current = 0
        self.last_percent = -1
    
    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        percent = int((self.current / self.total) * 100)
        
        # Log every 10% or at completion
        if percent != self.last_percent and (percent % 10 == 0 or self.current == self.total):
            self.logger.info(f"{self.description}: {percent}% ({self.current}/{self.total})")
            self.last_percent = percent
    
    def finish(self):
        """Mark as complete."""
        self.logger.info(f"{self.description}: Complete ({self.total}/{self.total})")


def log_system_info(logger: logging.Logger):
    """Log system and environment information."""
    import platform
    import sys
    
    logger.info("=" * 50)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 50)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 50)


def log_config_summary(logger: logging.Logger):
    """Log configuration summary."""
    from config import HARDWARE, SENSORS, MODEL
    
    logger.info("=" * 50)
    logger.info("CONFIGURATION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Sample Rate: {HARDWARE['sample_rate_hz']} Hz")
    logger.info(f"ADC Resolution: {HARDWARE['adc_resolution_bits']}-bit")
    logger.info(f"Sensors: {SENSORS['count']}")
    logger.info(f"Model: Random Forest ({MODEL['random_forest']['n_estimators']} trees)")
    logger.info("=" * 50)


# =============================================================================
# DECORATORS
# =============================================================================

def log_execution_time(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_execution_time()
        def my_function():
            pass
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger(func.__module__)
            start_time = time.time()
            log.debug(f"Starting {func.__name__}...")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                log.debug(f"Completed {func.__name__} in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                log.error(f"Failed {func.__name__} after {elapsed:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator


def log_exceptions(logger: Optional[logging.Logger] = None):
    """
    Decorator to log exceptions without swallowing them.
    
    Usage:
        @log_exceptions()
        def my_function():
            pass
    """
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator


if __name__ == '__main__':
    # Demo
    setup_logging(level='DEBUG')
    logger = get_logger(__name__)
    
    log_system_info(logger)
    log_config_summary(logger)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Progress logger demo
    progress = ProgressLogger(logger, 100, "Demo processing")
    for i in range(100):
        progress.update()
    progress.finish()
