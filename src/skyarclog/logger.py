"""SkyArcLog logger implementation."""

import logging
import warnings
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import traceback
import os

from .core.exceptions import LoggerConfigurationWarning, ConfigValidationError
from .config_manager import ConfigManager
from .core.plugin_manager import PluginManager

# Global logger instance
_GLOBAL_LOGGER = None

class SkyArcLogger:
    """Main logger class for SkyArcLog."""

    # Map string level names to numeric values
    _LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the logger.
        
        Args:
            config_path: Optional path to configuration file
        """
        self._config = {}
        self._formatters = {}
        self._listeners = {}
        self._plugin_manager = None
        
        if config_path:
            self.load_configuration(config_path)
        else:
            raise ValueError("Configuration path must be provided.")
        
        self._initialize_components()

    def load_configuration(self, config_path: str) -> None:
        """Load logger configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            ConfigValidationError: If configuration is invalid
        """
        from .config.validator import validate_configuration
        
        config_manager = ConfigManager(config_path)
        config = config_manager.load_configuration(config_path)
        
        # Validate configuration
        try:
            validate_configuration(config)
        except ConfigValidationError as e:
            raise ConfigValidationError(f"Invalid configuration: {e}")
        
        self._config = config
        self._initialize_components()

    def _initialize_components(self):
        """Initialize logging components based on configuration."""
        from .formatters import create_formatter
        from .listeners import create_listener

        # Initialize formatters
        formatters_config = self._config.get('formatters', {})
        for formatter_name, formatter_config in formatters_config.items():
            try:
                formatter = create_formatter(formatter_name, formatter_config)
                self._formatters[formatter_name] = formatter
            except Exception as e:
                warnings.warn(
                    f"Could not initialize formatter {formatter_name}: {e}",
                    LoggerConfigurationWarning
                )

        # Initialize listeners
        listeners_config = self._config.get('listeners', {})
        for listener_name, listener_config in listeners_config.items():
            try:
                if listener_config.get('enabled', True):
                    listener = create_listener(listener_name, listener_config)
                    self._listeners[listener_name] = listener
            except Exception as e:
                warnings.warn(
                    f"Could not initialize listener {listener_name}: {e}",
                    LoggerConfigurationWarning
                )

        # Set logging level
        loggers_config = self._config.get('loggers', {})
        root_logger_config = loggers_config.get('root', {})
        level_name = root_logger_config.get('level', 'WARNING').upper()
        self._level = self._LEVEL_MAP.get(level_name, logging.WARNING)

    def log(self, level: str, message: Any, **kwargs):
        """
        Log a message with the specified level and additional context.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **kwargs: Additional log context
        """
        # Convert string level to numeric level
        numeric_level = self._LEVEL_MAP.get(level.upper(), logging.INFO)
        
        # Apply formatters
        for formatter in self._formatters.values():
            # Convert bytes to string if necessary
            if isinstance(message, bytes):
                try:
                    message = message.decode('utf-8')
                except UnicodeDecodeError:
                    message = str(message)
            
            message = formatter.transform(message, **kwargs)
        
        # Send to listeners
        for listener in self._listeners.values():
            listener.log(numeric_level, message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.log('DEBUG', message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.log('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self.log('CRITICAL', message, **kwargs)

    def exception(self, message: str, exc_info: Optional[BaseException] = None, **kwargs):
        """
        Log an exception with error level.
        
        Args:
            message: Error message
            exc_info: Exception object or traceback
            **kwargs: Additional log context
        """
        # If no exception is provided, get the current exception
        if exc_info is None:
            exc_info = sys.exc_info()[1]
        
        # Add exception details to kwargs
        if exc_info:
            kwargs['exc_type'] = type(exc_info).__name__
            kwargs['exc_message'] = str(exc_info)
            kwargs['traceback'] = traceback.format_exc()
        
        # Log as an error
        self.log('ERROR', message, **kwargs)

    def close(self):
        """Close all listeners and flush any buffered logs."""
        for listener in self._listeners.values():
            listener.close()

def log(level: str, message: str, **kwargs) -> None:
    """
    Global logging function to log messages.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        **kwargs: Additional log context
    
    Raises:
        ConfigValidationError: If logger configuration is invalid
    """
    try:
        # Create a logger with a default configuration
        logger = SkyArcLogger(config_path=None)
        logger.log(level, message, **kwargs)
    except ConfigValidationError as e:
        # If configuration is invalid, prevent logging
        warnings.warn(f"Logging disabled due to configuration error: {e}", RuntimeWarning)
        # Optionally, log to stderr or a fallback mechanism
        print(f"[LOGGING DISABLED] {level}: {message}", file=sys.stderr)

def debug(message: str, **kwargs) -> None:
    """Log a debug message."""
    log('DEBUG', message, **kwargs)

def info(message: str, **kwargs) -> None:
    """Log an info message."""
    log('INFO', message, **kwargs)

def warning(message: str, **kwargs) -> None:
    """Log a warning message."""
    log('WARNING', message, **kwargs)

def error(message: str, **kwargs) -> None:
    """Log an error message."""
    log('ERROR', message, **kwargs)

def critical(message: str, **kwargs) -> None:
    """Log a critical message."""
    log('CRITICAL', message, **kwargs)

def configure(config_path: Optional[str] = None) -> SkyArcLogger:
    """
    Configure the logger with a given configuration file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Configured SkyArcLogger instance
    
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Import Path here to avoid potential circular imports
    from pathlib import Path
    from .config.validator import validate_configuration, ConfigValidationError
    
    # Ensure the config path is an absolute path if it's a relative path
    if config_path:
        # Convert to absolute path, handling both relative and absolute paths
        config_path = str(Path(config_path).resolve())
    
    def handle_config_change(new_config: Dict[str, Any]):
        """
        Handle configuration changes dynamically.
        
        Args:
            new_config: New configuration dictionary
        """
        try:
            # Validate the new configuration
            validate_configuration(new_config)
            
            # Reinitialize logger components based on new configuration
            logger = SkyArcLogger(config_path)
            
            # Update global logger if needed
            global _GLOBAL_LOGGER
            _GLOBAL_LOGGER = logger
            
            # Log configuration change
            if new_config:
                warnings.warn(
                    f"Logger reconfigured.", 
                    LoggerConfigurationWarning
                )
        
        except ConfigValidationError as e:
            warnings.warn(
                f"Failed to apply new configuration: {e}", 
                LoggerConfigurationWarning
            )
    
    try:
        # Create a config manager with change handling
        from .config_manager import ConfigManager
        config_manager = ConfigManager(config_path, on_config_change=handle_config_change)
        
        # Create and return the logger instance
        logger = SkyArcLogger(config_path)
        
        # Validate the configuration
        validate_configuration(logger._config)
        
        # Set as global logger
        global _GLOBAL_LOGGER
        _GLOBAL_LOGGER = logger
        
        return logger
    
    except ConfigValidationError as e:
        # Raise configuration validation errors
        raise ConfigValidationError(f"Invalid logging configuration: {e}") from e
    
    except Exception as e:
        # Log the configuration error
        warnings.warn(f"Failed to configure logger: {e}", LoggerConfigurationWarning)
        
        # Return a default logger with a console listener
        from .listeners import ConsoleListener
        
        default_logger = SkyArcLogger()
        console_listener = ConsoleListener()
        default_logger._listeners['console'] = console_listener
        
        return default_logger
