"""SkyArcLog logger implementation."""

import logging
import warnings
from typing import Dict, Any, Optional, List
from .core.plugin_manager import PluginManager
from .config_manager import ConfigManager

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
        self._config_manager = ConfigManager(config_path)
        self._plugin_manager = PluginManager()
        self._listeners = {}
        self._transformers = {}
        self._level = logging.INFO  # Default level
        self._handlers_config = {}
        self._initialize_components()

    def _validate_logger_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validate and normalize logger configuration.
        
        Supports both list and dictionary handler configurations.
        
        Args:
            config: Full logger configuration dictionary
        """
        logger_configs = config.get('loggers', {})
        root_config = logger_configs.get('root', {})
        
        # Get root logger level
        root_level_name = root_config.get('level', 'INFO').upper()
        root_level_value = self._LEVEL_MAP.get(root_level_name, logging.INFO)
        
        # Normalize handlers configuration
        handlers = root_config.get('handlers', [])
        
        # Reset handlers configuration
        self._handlers_config = {}
        
        if isinstance(handlers, list):
            # List of listeners: apply to all levels >= root level
            for level_name, level_value in self._LEVEL_MAP.items():
                if level_value >= root_level_value:
                    self._handlers_config[level_name] = handlers
        
        elif isinstance(handlers, dict):
            # Dictionary of level-specific handlers
            for level_name, level_handlers in handlers.items():
                level_name = level_name.upper()
                
                # Validate log level
                if level_name not in self._LEVEL_MAP:
                    warnings.warn(
                        f"Invalid log level: {level_name}. This handler configuration will be ignored.",
                        LoggerConfigurationWarning
                    )
                    continue
                
                level_value = self._LEVEL_MAP[level_name]
                
                # Only keep handlers for levels >= root logger level
                if level_value >= root_level_value:
                    self._handlers_config[level_name] = level_handlers

    def _get_handlers_for_level(self, level: str) -> List[str]:
        """
        Retrieve handlers for a specific log level.
        
        Implements level-based handler routing with override capabilities.
        
        Args:
            level: Current log level
        
        Returns:
            List of applicable handler names
        """
        # Normalize level
        level = level.upper()
        
        # Validate current log level
        if level not in self._LEVEL_MAP:
            return []
        
        # Get root logger configuration
        root_config = self._config_manager.get_config().get('loggers', {}).get('root', {})
        root_level_name = root_config.get('level', 'INFO').upper()
        root_level_value = self._LEVEL_MAP.get(root_level_name, logging.INFO)
        current_level_value = self._LEVEL_MAP[level]
        
        # If current log level is lower than root logger level, return empty list
        if current_level_value < root_level_value:
            return []
        
        # Collect applicable handlers
        applicable_handlers = []
        
        # Priority 1: Exact level handlers
        if level in self._handlers_config:
            applicable_handlers.extend(self._handlers_config[level])
        
        # Priority 2: Handlers for levels less than current level
        for config_level, handlers in self._handlers_config.items():
            config_level_value = self._LEVEL_MAP[config_level]
            
            # Add handlers for levels less than current level
            if config_level_value < current_level_value:
                applicable_handlers.extend(handlers)
        
        return list(set(applicable_handlers))

    def _initialize_components(self) -> None:
        """Initialize listeners and transformers from configuration."""
        config = self._config_manager.get_config()
        
        # Validate logger configuration before processing
        self._validate_logger_configuration(config)
        
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

        # Get handlers for this specific log level
        handlers = self._get_handlers_for_level(level)
        
        # Get application name from configuration, default to 'Application'
        config = self._config_manager.get_config()
        app_name = config.get('name', 'Application')
        
        log_data = {
            'level': level,
            'message': message,
            'application': app_name,  # Add application name to log data
            **kwargs
        }

        for handler_name in handlers:
            listener = self._listeners.get(handler_name)
            if listener:
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
        """Clean up and close all listeners."""
        for listener in self._listeners.values():
            try:
                listener.close()
            except Exception as e:
                logging.error(f"Error closing listener: {str(e)}")
        self._listeners.clear()

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
