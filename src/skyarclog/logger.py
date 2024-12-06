"""SkyArcLog main logger module."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from queue import Queue
from pythonjsonlogger import jsonlogger

from skyarclog.handlers.base_handler import BaseHandler
from skyarclog.handlers.core import (
    create_console_handler,
    create_file_handler,
    create_memory_handler,
    create_queue_handler,
    create_blob_handler,
    create_appinsights_handler,
    create_sql_handler
)
from skyarclog.config.validator import validate_handler_config, ConfigValidationError


class SkyArcLogger:
    """Main logger class for SkyArcLog."""

    def __init__(
        self,
        name: str,
        handlers_config: Optional[List[Dict]] = None,
        config_manager=None
    ):
        """Initialize the logger.
        
        Args:
            name (str): Logger name
            handlers_config (Optional[List[Dict]]): List of handler configurations
            config_manager: Configuration manager instance
            
        Raises:
            ConfigValidationError: If handler configuration is invalid
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Allow all logs, filter at handler level
        
        self.base_handler = BaseHandler(config_manager)
        self._setup_handlers(handlers_config or [])

    def _setup_handlers(self, handlers_config: List[Dict]) -> None:
        """Set up handlers based on configuration.
        
        Args:
            handlers_config (List[Dict]): List of handler configurations
            
        Raises:
            ConfigValidationError: If handler configuration is invalid
        """
        for handler_config in handlers_config:
            handler_type = handler_config.get('type')
            if not handler_type:
                raise ConfigValidationError("Handler configuration must specify 'type'")

            # Validate handler configuration
            validate_handler_config(handler_type, handler_config)
            
            # Create and add handler
            handler = self.base_handler.create_handler(handler_type, handler_config)
            if handler:
                self.logger.addHandler(handler)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception message."""
        self.logger.exception(msg, *args, **kwargs)

    def log(self, level: Union[int, str], msg: str, *args, **kwargs) -> None:
        """Log a message with specified level."""
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        self.logger.log(level, msg, *args, **kwargs)

    def close(self) -> None:
        """Close the logger and clean up resources."""
        self.base_handler.stop_queue_listeners()
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
