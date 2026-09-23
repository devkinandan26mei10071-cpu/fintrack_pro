"""
Logging subsystem for FinTrack Pro.
Provides structured, rotating file logging and clean console output.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "fintrack", log_file: str = "logs/fintrack.log", level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a thread-safe logger with rotating file and optional console handler.
    
    Args:
        name: Name of the logger instance.
        log_file: Path to the log file.
        level: Minimum logging level.
        
    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File handler with rotation (max 2MB per file, keeping 3 backups)
    file_handler = RotatingFileHandler(
        str(log_path),
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    return logger


# Default global logger
app_logger = setup_logger()
