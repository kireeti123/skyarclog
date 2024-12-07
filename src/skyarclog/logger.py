"""SkyArcLog logger implementation."""

import logging
from typing import Dict, Any, Optional
from .core.plugin_manager import PluginManager
from .config_manager import ConfigManager

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
        self._config_manager = ConfigManager(config_path)
        self._plugin_manager = PluginManager()
        self._listeners = {}
        self._transformers = {}
        self._level = logging.INFO  # Default level
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize listeners and transformers from configuration."""
        config = self._config_manager.get_config()
        
        # Initialize transformers first
        transformer_configs = config.get('transformers', {})
        for name, transformer_config in transformer_configs.items():
            if transformer_config.get('enabled', True):
                transformer = self._plugin_manager.create_transformer(
                    transformer_config['type'],
                    transformer_config.get('config', {})
                )
                if transformer:
                    self._transformers[name] = transformer

        # Initialize listeners
        listener_configs = config.get('listeners', {})
        for name, listener_config in listener_configs.items():
            if listener_config.get('enabled', True):
                # Get associated transformer if specified
                transformer = None
                transformer_name = listener_config.get('transformer')
                if transformer_name:
                    transformer = self._transformers.get(transformer_name)

                listener = self._plugin_manager.create_listener(name, {
                    **listener_config,
                    'transformer': transformer
                })
                if listener:
                    self._listeners[name] = listener

        # Set log level from configuration
        logger_configs = config.get('loggers', {})
        root_config = logger_configs.get('root', {})
        level_name = root_config.get('level', 'INFO')
        self._level = self._LEVEL_MAP.get(level_name, logging.INFO)

    def _should_log(self, level: str) -> bool:
        """Check if a message at the given level should be logged.
        
        Args:
            level: Log level to check
            
        Returns:
            bool: True if the message should be logged, False otherwise
        """
        level_value = self._LEVEL_MAP.get(level, logging.NOTSET)
        return level_value >= self._level

    def log(self, level: str, message: str, **kwargs) -> None:
        """Log a message.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional log data
        """
        if not self._should_log(level):
            return

        log_data = {
            'level': level,
            'message': message,
            **kwargs
        }

        for listener in self._listeners.values():
            try:
                listener.handle(log_data)
            except Exception as e:
                logging.error(f"Error in listener {listener.__class__.__name__}: {str(e)}")

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

    def close(self) -> None:
        """Close all listeners."""
        for listener in self._listeners.values():
            try:
                listener.close()
            except Exception as e:
                logging.error(f"Error closing listener {listener.__class__.__name__}: {str(e)}")
