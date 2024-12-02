"""
Configuration loader for SkyArcLog.
Handles loading and validation of the centralized logging configuration.
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path
import importlib

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass

class ConfigLoader:
    """
    Loads and validates the centralized logging configuration.
    Supports environment variable substitution and configuration inheritance.
    """
    
    DEFAULT_CONFIG_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "logging_config.json"
    )
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Optional path to the configuration file.
                        If not provided, uses the default config path.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """
        Load and validate the configuration.
        
        Returns:
            Dict containing the validated configuration.
            
        Raises:
            ConfigurationError: If configuration is invalid or cannot be loaded.
        """
        try:
            # Load base configuration
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                
            # Validate version
            if 'version' not in self.config:
                raise ConfigurationError("Configuration version is required")
                
            # Process environment variables
            self._process_env_vars(self.config)
            
            # Validate configuration
            self._validate_config()
            
            return self.config
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {str(e)}")
            
    def _process_env_vars(self, config: Dict[str, Any]) -> None:
        """
        Process environment variables in configuration values.
        Replaces ${ENV_VAR} with the corresponding environment variable value.
        """
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    config[key] = os.environ.get(env_var, value)
                elif isinstance(value, (dict, list)):
                    self._process_env_vars(value)
        elif isinstance(config, list):
            for i, value in enumerate(config):
                if isinstance(value, (dict, list)):
                    self._process_env_vars(value)
                    
    def _validate_config(self) -> None:
        """
        Validate the configuration structure and required fields.
        
        Raises:
            ConfigurationError: If configuration is invalid.
        """
        required_sections = ['formatters', 'listeners', 'async_worker']
        for section in required_sections:
            if section not in self.config:
                raise ConfigurationError(f"Required section '{section}' not found in configuration")
                
        # Validate formatters
        for name, formatter in self.config['formatters'].items():
            if 'class' not in formatter:
                raise ConfigurationError(f"Formatter '{name}' missing required 'class' field")
            self._validate_class_exists(formatter['class'])
                
        # Validate listeners
        for name, listener in self.config['listeners'].items():
            if listener.get('enabled', False):
                if 'class' not in listener:
                    raise ConfigurationError(f"Listener '{name}' missing required 'class' field")
                if 'formatter' not in listener:
                    raise ConfigurationError(f"Listener '{name}' missing required 'formatter' field")
                if listener['formatter'] not in self.config['formatters']:
                    raise ConfigurationError(
                        f"Listener '{name}' references undefined formatter '{listener['formatter']}'"
                    )
                self._validate_class_exists(listener['class'])
                
        # Validate async worker configuration
        async_worker = self.config['async_worker']
        required_worker_fields = ['num_workers', 'queue_size', 'batch_size']
        for field in required_worker_fields:
            if field not in async_worker:
                raise ConfigurationError(f"Async worker missing required field '{field}'")
                
    def _validate_class_exists(self, class_path: str) -> None:
        """
        Validate that a class exists in the Python path.
        
        Args:
            class_path: Fully qualified class path (e.g., 'package.module.ClassName')
            
        Raises:
            ConfigurationError: If class cannot be imported
        """
        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            if not hasattr(module, class_name):
                raise ConfigurationError(f"Class '{class_name}' not found in module '{module_path}'")
        except (ImportError, AttributeError) as e:
            raise ConfigurationError(f"Failed to import class '{class_path}': {str(e)}")
            
    def get_listener_config(self, listener_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific listener.
        
        Args:
            listener_name: Name of the listener
            
        Returns:
            Dict containing the listener configuration
            
        Raises:
            ConfigurationError: If listener is not found or not enabled
        """
        if listener_name not in self.config['listeners']:
            raise ConfigurationError(f"Listener '{listener_name}' not found in configuration")
            
        listener = self.config['listeners'][listener_name]
        if not listener.get('enabled', False):
            raise ConfigurationError(f"Listener '{listener_name}' is not enabled")
            
        return listener
        
    def get_formatter_config(self, formatter_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific formatter.
        
        Args:
            formatter_name: Name of the formatter
            
        Returns:
            Dict containing the formatter configuration
            
        Raises:
            ConfigurationError: If formatter is not found
        """
        if formatter_name not in self.config['formatters']:
            raise ConfigurationError(f"Formatter '{formatter_name}' not found in configuration")
            
        return self.config['formatters'][formatter_name]
        
    def get_async_worker_config(self) -> Dict[str, Any]:
        """
        Get async worker configuration.
        
        Returns:
            Dict containing the async worker configuration
        """
        return self.config['async_worker']
        
    def get_security_config(self) -> Dict[str, Any]:
        """
        Get security configuration.
        
        Returns:
            Dict containing the security configuration
        """
        return self.config.get('security', {})
        
    def get_performance_config(self) -> Dict[str, Any]:
        """
        Get performance configuration.
        
        Returns:
            Dict containing the performance configuration
        """
        return self.config.get('performance', {})
        
    def get_monitoring_config(self) -> Dict[str, Any]:
        """
        Get monitoring configuration.
        
        Returns:
            Dict containing the monitoring configuration
        """
        return self.config.get('monitoring', {})
