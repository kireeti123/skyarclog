"""SkyArcLog package."""

import importlib
import warnings
import logging

# Global logger configuration
__all__ = [
    'log'
]

# Global logger instance
_GLOBAL_LOGGER = None

class Log:
    """
    A wrapper class to provide intuitive logging methods.
    Allows logging using methods like log.debug(), log.info(), etc.
    """
    def __init__(self):
        self._logger = None

    def _ensure_logger(self):
        """Ensure a global logger is created."""
        if self._logger is None:
            # Use Python's built-in logging as a fallback
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
            
            # Add a console handler if no handlers exist
            if not self._logger.handlers:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                self._logger.addHandler(console_handler)

    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self._ensure_logger()
        self._logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log an info message."""
        self._ensure_logger()
        self._logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self._ensure_logger()
        self._logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log an error message."""
        self._ensure_logger()
        self._logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log a critical message."""
        self._ensure_logger()
        self._logger.critical(message, extra=kwargs)

# Create a global log instance
log = Log()

# Prevent further imports during initialization
__import__ = None
