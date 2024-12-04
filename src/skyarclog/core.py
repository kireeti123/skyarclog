"""
Core module for skyarclog.
"""
import os
import json
import logging
from typing import Optional, Dict, Any

class LogManager:
    """Singleton class to manage logging configuration and setup."""
    _instance = None
    _initialized = False
    _config = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._config = None
            self._logger = None

    @staticmethod
    def _get_config_path(env: str) -> str:
        """Get configuration file path based on environment."""
        # Try multiple config locations
        config_locations = [
            # Current directory
            os.path.join(os.getcwd(), 'config'),
            # Package config directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'),
            # User's home directory
            os.path.join(os.path.expanduser('~'), '.skyarclog', 'config')
        ]
        
        config_file = f'custom_logging_{env}.json'
        default_file = 'custom_logging.json'
        
        # Try environment-specific config in all locations
        for config_dir in config_locations:
            config_path = os.path.join(config_dir, config_file)
            if os.path.exists(config_path):
                return config_path
        
        # Try default config in all locations
        for config_dir in config_locations:
            config_path = os.path.join(config_dir, default_file)
            if os.path.exists(config_path):
                return config_path
        
        raise FileNotFoundError(
            f"No logging configuration found for environment: {env}. "
            f"Looked in: {', '.join(config_locations)}"
        )

    def _load_config(self, env: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = self._get_config_path(env)
        with open(config_path, 'r') as f:
            return json.load(f)

    def setup(self, env: str = 'dev') -> 'LogManager':
        """Setup logging with the specified environment configuration."""
        self._config = self._load_config(env)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self._config.get('log_level', 'INFO')),
            format='%(levelname)s:%(name)s:%(message)s'
        )
        
        # Store application name for later use
        self._logger = logging.getLogger(self._config['application']['name'])
        
        return self

    def get_logger(self) -> logging.Logger:
        """Get the logger instance with application name from config."""
        if not self._logger:
            raise RuntimeError("Logger not initialized. Call setup() first.")
        return self._logger

    @property
    def config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        if not self._config:
            raise RuntimeError("Configuration not loaded. Call setup() first.")
        return self._config

def setup_logging(env: str = 'dev') -> LogManager:
    """
    Initialize logging with the specified environment configuration.
    
    Args:
        env: Environment name ('dev', 'prod', etc.)
    
    Returns:
        LogManager instance for further configuration
    """
    return LogManager().setup(env)
