"""SkyArcLog logger implementation."""

import logging
import warnings
from typing import Dict, Any, Optional, List
from pathlib import Path

# Lazy import to prevent circular dependencies
def _lazy_import_config_manager():
    from .config_manager import ConfigManager
    return ConfigManager

def _lazy_import_plugin_manager():
    from .core.plugin_manager import PluginManager
    return PluginManager

class LoggerConfigurationWarning(Warning):
    """Custom warning for logger configuration issues."""
    pass

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
        # Lazy import to prevent circular dependencies
        ConfigManager = _lazy_import_config_manager()
        PluginManager = _lazy_import_plugin_manager()

        # Initialize configuration
        self._config_manager = ConfigManager(config_path)
        self._config = self._config_manager.get_config()
        
        # Initialize plugin manager
        self._plugin_manager = PluginManager()
        
        # Initialize logging components
        self._listeners = {}
        self._transformers = {}
        self._level = logging.INFO  # Default level
        self._handlers_config = {}
        
        # Set up logging
        self._initialize_components()

    def _initialize_components(self):
        """Initialize logging components based on configuration."""
        # Configure listeners
        listeners = self._config.get('listeners', {})
        for listener_name, listener_config in listeners.items():
            if listener_config.get('enabled', False):
                try:
                    # Use plugin manager to create and configure listener
                    listener = self._plugin_manager.create_listener(
                        listener_name, 
                        listener_config
                    )
                    self._listeners[listener_name] = listener
                except Exception as e:
                    warnings.warn(
                        f"Could not initialize listener {listener_name}: {e}", 
                        LoggerConfigurationWarning
                    )

        # Configure transformers
        transformers = self._config.get('transformers', {})
        for transformer_name, transformer_config in transformers.items():
            try:
                # Use plugin manager to create and configure transformer
                transformer = self._plugin_manager.create_transformer(
                    transformer_name, 
                    transformer_config
                )
                self._transformers[transformer_name] = transformer
            except Exception as e:
                warnings.warn(
                    f"Could not initialize transformer {transformer_name}: {e}", 
                    LoggerConfigurationWarning
                )

    def log(self, level: str, message: str, **kwargs):
        """
        Log a message with the specified level and additional context.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **kwargs: Additional log context
        """
        # Convert string level to numeric level
        numeric_level = self._LEVEL_MAP.get(level.upper(), logging.INFO)
        
        # Apply transformers
        for transformer in self._transformers.values():
            message = transformer.transform(message, **kwargs)
        
        # Send to listeners
        for listener in self._listeners.values():
            listener.log(numeric_level, message, **kwargs)

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
    """
    # Create a logger with a default configuration
    logger = SkyArcLogger(config_path=None)
    logger.log(level, message, **kwargs)

def configure(config_path: Optional[str] = None) -> None:
    """
    Configure the logger with a given configuration file.
    
    Args:
        config_path: Path to the configuration file
    """
    # If no config path is provided, use the default configuration
    logger = SkyArcLogger(config_path)
    # Additional configuration logic can be added here if needed
