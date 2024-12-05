"""
Core module for skyarclog.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from logging.handlers import RotatingFileHandler
from .listeners import ConsoleListener, FileListener, AzureBlobListener, AzureAppInsightsListener, MSSQLListener
from .formatters import JSONFormatter

class LogManager:
    """Singleton class to manage logging configuration and setup."""
    _instance = None
    _initialized = False
    _config = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._config = None
            self._loggers = {}

    @staticmethod
    def _get_config_path(env: str) -> str:
        """Get configuration file path based on environment."""
        config_locations = [
            os.path.join(os.getcwd(), 'config'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'),
            os.path.join(os.path.expanduser('~'), '.skyarclog', 'config')
        ]
        
        config_file = f'custom_logging_{env}.json'
        default_file = 'custom_logging.json'
        
        for config_dir in config_locations:
            config_path = os.path.join(config_dir, config_file)
            if os.path.exists(config_path):
                return config_path
            
        for config_dir in config_locations:
            config_path = os.path.join(config_dir, default_file)
            if os.path.exists(config_path):
                return config_path
        
        raise FileNotFoundError("No logging configuration file found")

    def _configure_listener(self, logger: logging.Logger, handler_name: str, handler_config: Dict[str, Any]) -> None:
        """Configure a specific listener/handler for a logger."""
        handler = None
        formatter = JSONFormatter() if handler_config.get('format') == 'json' else logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if handler_name == 'console':
            handler = ConsoleListener()
        elif handler_name == 'file':
            handler = FileListener(
                filename=handler_config.get('path', 'app.log'),
                maxBytes=self._parse_size(handler_config.get('max_size', '100MB')),
                backupCount=handler_config.get('backup_count', 5)
            )
        elif handler_name == 'azure-blob':
            handler = AzureBlobListener(
                connection_string=os.getenv(handler_config.get('container_connection_string', ''))
            )
        elif handler_name == 'azure-appinsights':
            handler = AzureAppInsightsListener(
                instrumentation_key=os.getenv(handler_config.get('instrumentation_key', ''))
            )
        elif handler_name == 'ms-sql':
            handler = MSSQLListener(
                connection_string=os.getenv(handler_config.get('connection_string', ''))
            )

        if handler:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '500MB') to bytes."""
        units = {'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
        size = size_str.strip()
        for unit in units:
            if size.endswith(unit):
                return int(float(size[:-len(unit)]) * units[unit])
        return int(size)

    def _setup_logger(self, name: str, config: Dict[str, Any]) -> logging.Logger:
        """Set up a specific logger with its configuration."""
        logger = logging.getLogger(config.get('qualname', name))
        logger.setLevel(config.get('level', 'INFO'))
        logger.propagate = config.get('propagate', True)

        # Configure handlers
        for handler_name in config.get('handlers', []):
            if handler_name in self._config['listeners']:
                self._configure_listener(logger, handler_name, self._config['listeners'][handler_name])

        return logger

    def setup_logging(self, env: str = 'dev') -> 'LogManager':
        """Initialize logging with the specified environment configuration."""
        config_path = self._get_config_path(env)
        
        with open(config_path, 'r') as f:
            self._config = json.load(f)

        # Configure root logger
        root_config = self._config['loggers'].get('root', {})
        root_logger = self._setup_logger('root', root_config)
        self._loggers['root'] = root_logger

        # Configure other loggers
        for logger_name, logger_config in self._config['loggers'].items():
            if logger_name != 'root':
                self._loggers[logger_name] = self._setup_logger(logger_name, logger_config)

        return self

    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a configured logger by name."""
        if name is None:
            return self._loggers.get('root', logging.getLogger())
        
        # Try to find exact match
        if name in self._loggers:
            return self._loggers[name]
        
        # Try to find parent logger
        parts = name.split('.')
        while parts:
            parent_name = '.'.join(parts[:-1])
            if parent_name in self._loggers:
                logger = logging.getLogger(name)
                logger.parent = self._loggers[parent_name]
                return logger
            parts.pop()
        
        # Fallback to root logger
        return self._loggers.get('root', logging.getLogger(name))

# Global function for easy access
def get_logger(name: str = None) -> logging.Logger:
    """Get a configured logger by name."""
    return LogManager().get_logger(name)
