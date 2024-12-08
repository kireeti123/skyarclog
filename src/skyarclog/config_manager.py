"""Configuration manager for SkyArcLog."""

import json
import os
import logging
import threading
import time
import uuid
from typing import Any, Dict, Optional, Union, Callable
from pathlib import Path
from dotenv import load_dotenv
from .config.validator import validate_configuration, ConfigValidationError

# Optional Azure imports
try:
    from azure.identity import ClientSecretCredential
    from azure.keyvault.secrets import SecretClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    # Type aliases for when Azure is not available
    SecretClient = Any
    ClientSecretCredential = Any

class ConfigManager:
    """Manages configuration and secrets for the logging framework."""
    
    DEFAULT_CONFIG = {
        "version": 1.0,
        "name": "SkyArcLog Default App",
        "transformers": {},
        "listeners": {
            "console": {
                "enabled": True,
                "format": "text",
                "colors": {
                    "enabled": True,
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bold"
                },
                "output": "stdout",
                "show_timestamp": True,
                "timestamp_format": "%Y-%m-%d %H:%M:%S.%f",
                "show_level": True,
                "show_thread": False,
                "show_process": False
            }
        },
        "loggers": {
            "root": {
                "level": "INFO",
                "handlers": ["console"]
            }
        }
    }

    def __init__(self, config_path: Optional[str] = None, 
                 on_config_change: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize configuration manager with dynamic reloading and change tracking.
        
        Args:
            config_path: Optional path to configuration file
            on_config_change: Optional callback function when configuration changes
        """
        # Use default configuration if no path is provided
        if config_path is None:
            config_path = Path(__file__).parent / 'skyarclog_logging.json'
        
        # Ensure config_path is a Path object
        self.config_path = Path(config_path)
        
        # Configuration state
        self._config: Dict[str, Any] = {}
        self._last_modified: float = 0
        self._lock = threading.Lock()
        
        # Configuration change callback
        self._on_config_change = on_config_change
        
        # Configuration reload settings
        self._auto_reload_enabled = True
        self._reload_interval = 5.0  # seconds
        
        # Load initial configuration
        self._load_config()
        
        # Start configuration monitoring thread
        self._start_config_monitor()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize secret client
        self._secret_client = self._initialize_keyvault_client()
        
        # Cache for secrets
        self._secrets_cache: Dict[str, str] = {}

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file, with error handling and default fallback.
        
        Returns:
            Loaded configuration dictionary
        """
        try:
            # Check if configuration file exists
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            # Get last modified time
            current_modified = os.path.getmtime(self.config_path)
            
            # Only reload if file has changed
            if current_modified > self._last_modified:
                with open(self.config_path, 'r') as f:
                    new_config = json.load(f)
                
                try:
                    # Validate configuration
                    validate_configuration(new_config)
                    
                    # Thread-safe config update
                    with self._lock:
                        # Update configuration
                        self._config = new_config
                        self._last_modified = current_modified
                    
                    # Optional: Log configuration reload
                    print(f"Configuration reloaded from {self.config_path}")
                
                except ConfigValidationError as validation_error:
                    print(f"Configuration validation failed: {validation_error}")
                    return self.DEFAULT_CONFIG
            
            return self._config
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Log error and return default configuration
            print(f"Error loading configuration: {e}")
            return self.DEFAULT_CONFIG
    
    def _start_config_monitor(self):
        """
        Start a background thread to monitor configuration file for changes.
        """
        def monitor_config():
            while self._auto_reload_enabled:
                try:
                    self._load_config()
                except Exception as e:
                    print(f"Configuration monitoring error: {e}")
                
                # Sleep between checks
                time.sleep(self._reload_interval)
        
        # Start monitoring thread as a daemon
        monitor_thread = threading.Thread(target=monitor_config, daemon=True)
        monitor_thread.start()
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration, ensuring thread safety.
        
        Returns:
            Current configuration dictionary
        """
        with self._lock:
            return self._config.copy()
    
    def reload_config(self):
        """
        Manually trigger configuration reload.
        """
        self._load_config()
    
    def set_reload_interval(self, interval: float):
        """
        Set the configuration reload interval.
        
        Args:
            interval: Reload interval in seconds
        """
        if interval < 1.0:
            raise ValueError("Reload interval must be at least 1 second")
        
        self._reload_interval = interval
    
    def disable_auto_reload(self):
        """
        Disable automatic configuration reloading.
        """
        self._auto_reload_enabled = False
    
    def enable_auto_reload(self):
        """
        Enable automatic configuration reloading.
        """
        self._auto_reload_enabled = True
        self._start_config_monitor()
    
    def _initialize_keyvault_client(self) -> Optional[SecretClient]:
        """Initialize Azure Key Vault client using credentials from environment."""
        if not AZURE_AVAILABLE:
            return None
        
        required_vars = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'AZURE_KEYVAULT_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return None
        
        # Create credentials and secret client
        credential = ClientSecretCredential(
            tenant_id=os.getenv('AZURE_TENANT_ID'),
            client_id=os.getenv('AZURE_CLIENT_ID'),
            client_secret=os.getenv('AZURE_CLIENT_SECRET')
        )
        
        return SecretClient(
            vault_url=os.getenv('AZURE_KEYVAULT_URL'),
            credential=credential
        )

    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve a secret from Azure Key Vault or environment variables.
        
        Args:
            secret_name: Name of the secret to retrieve
        
        Returns:
            Secret value or None if not found
        """
        # Check cache first
        if secret_name in self._secrets_cache:
            return self._secrets_cache[secret_name]
        
        # Try environment variables
        env_secret = os.getenv(secret_name)
        if env_secret:
            self._secrets_cache[secret_name] = env_secret
            return env_secret
        
        # Try Azure Key Vault
        if self._secret_client:
            try:
                secret = self._secret_client.get_secret(secret_name)
                self._secrets_cache[secret_name] = secret.value
                return secret.value
            except Exception as e:
                logging.warning(f"Could not retrieve secret {secret_name} from Azure Key Vault: {e}")
        
        return None

    def process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process configuration dictionary, resolving any secret references.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Processed configuration dictionary
        """
        def process_value(value: Any) -> Any:
            if isinstance(value, str) and value.startswith('@secret:'):
                secret_name = value[8:]  # Remove '@secret:' prefix
                return self.get_secret(secret_name, value)
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(item) for item in value]
            return value
        
        return process_value(config)

    def load_config(self) -> Dict[str, Any]:
        """Load and process configuration from file.
        
        Returns:
            Processed configuration dictionary
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path) as f:
            config = json.load(f)
        
        return self.process_config(config)

    def refresh_secrets(self) -> None:
        """Refresh all cached secrets from Key Vault."""
        if AZURE_AVAILABLE and self._secret_client:
            self._secrets_cache.clear()

    def get_connection_string(self, service_name: str) -> str:
        """Get a connection string for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Connection string for the service
        """
        if not AZURE_AVAILABLE or not self._secret_client:
            return ""
        
        secret_name = f"{service_name.upper()}-CONNECTION-STRING"
        return self.get_secret(secret_name, "")

    def create_default_config_file(self):
        """
        Create a default configuration file if it doesn't exist.
        """
        if not self.config_path.exists():
            default_config = self.DEFAULT_CONFIG.copy()
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            print(f"Created default configuration file at {self.config_path}")
    
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._secrets_cache.clear()
