"""
Configuration module for advanced logging framework.
"""

import os
import json
from typing import Any, Dict, Optional
from datetime import timedelta

# Default configuration
default_config = {
    "application": {
        "name": "skyarclog-app",  # Default application name
        "version": "1.0.0"
    },
    "log_level": "INFO",
    "formatters": ["json"],
    "security": {
        "encryption": {
            "enabled": True,
            "type": "aes-gcm",
            "key_rotation_interval": "7d"
        },
        "signatures": {
            "enabled": True,
            "key_rotation_interval": "30d"
        },
        "validation": {
            "enabled": True,
            "chain_size": 100,
            "export_interval": "1h",
            "export_path": "logs/chain.json"
        }
    },
    "listeners": {
        "console": {
            "enabled": True,
            "format": "json"
        },
        "file": {
            "enabled": False,
            "path": "logs/app.log",
            "max_size": "100MB",
            "backup_count": 5
        }
    }
}

class LoggingConfig:
    """Configuration management for logging framework."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize logging configuration.
        
        Args:
            config_file: Optional path to JSON configuration file.
        """
        self.config = default_config.copy()
        
        if config_file:
            self.load_config(config_file)
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mapping = {
            "LOG_LEVEL": ("log_level", str),
            "LOG_FORMATTERS": ("formatters", lambda x: x.split(",")),
            "ENCRYPTION_TYPE": ("security.encryption.type", str),
            "ENCRYPTION_KEY_ROTATION": ("security.encryption.key_rotation_interval", str),
            "SIGNATURE_KEY_ROTATION": ("security.signatures.key_rotation_interval", str),
            "VALIDATION_CHAIN_SIZE": ("security.validation.chain_size", int),
            "VALIDATION_EXPORT_INTERVAL": ("security.validation.export_interval", str),
            "VALIDATION_EXPORT_PATH": ("security.validation.export_path", str)
        }
        
        for env_var, (config_path, type_converter) in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                self.set_value(config_path, type_converter(value))
    
    def load_config(self, config_file: str):
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to JSON configuration file.
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading config file: {e}")
    
    def save_config(self, config_file: str):
        """
        Save configuration to JSON file.
        
        Args:
            config_file: Path to save configuration file.
        """
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.
        
        Args:
            path: Dot-notation path to configuration value.
            default: Default value if path not found.
            
        Returns:
            Configuration value or default.
        """
        current = self.config
        for key in path.split('.'):
            if isinstance(current, dict):
                current = current.get(key, default)
            else:
                return default
        return current
    
    def set_value(self, path: str, value: Any):
        """
        Set configuration value by dot-notation path.
        
        Args:
            path: Dot-notation path to configuration value.
            value: Value to set.
        """
        keys = path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def parse_duration(self, duration_str: str) -> timedelta:
        """
        Parse duration string to timedelta.
        
        Args:
            duration_str: Duration string (e.g., "7d", "24h", "30m").
            
        Returns:
            Timedelta object.
        """
        unit = duration_str[-1]
        value = int(duration_str[:-1])
        
        if unit == 'd':
            return timedelta(days=value)
        elif unit == 'h':
            return timedelta(hours=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        else:
            raise ValueError(f"Invalid duration unit: {unit}")
    
    def get_rotation_interval(self, key_type: str) -> timedelta:
        """
        Get key rotation interval.
        
        Args:
            key_type: Type of key ("encryption" or "signature").
            
        Returns:
            Rotation interval as timedelta.
        """
        path = f"security.{key_type}.key_rotation_interval"
        duration_str = self.get_value(path)
        return self.parse_duration(duration_str)
    
    def get_export_interval(self) -> timedelta:
        """
        Get validation chain export interval.
        
        Returns:
            Export interval as timedelta.
        """
        duration_str = self.get_value("security.validation.export_interval")
        return self.parse_duration(duration_str)
    
    def get_security_config(self) -> Dict[str, Any]:
        """
        Get complete security configuration.
        
        Returns:
            Security configuration dictionary.
        """
        return self.config["security"]
    
    def get_listener_config(self, listener_name: str) -> Dict[str, Any]:
        """
        Get listener configuration.
        
        Args:
            listener_name: Name of the listener.
            
        Returns:
            Listener configuration dictionary.
        """
        return self.config["listeners"].get(listener_name, {})

def configure_logging(config_file: Optional[str] = None) -> LoggingConfig:
    """
    Create and return a logging configuration
    
    :param config_file: Optional path to JSON configuration file
    :return: LoggingConfig instance
    """
    return LoggingConfig(config_file)
