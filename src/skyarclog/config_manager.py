"""Configuration manager for SkyArcLog."""

import json
import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dotenv import load_dotenv

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
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Use default configuration if no path is provided
        if config_path is None:
            config_path = Path(__file__).parent / 'skyarclog_logging.json'
        
        # Ensure config_path is a Path object
        self.config_path = Path(config_path)
        
        # Load configuration
        self.config = self._load_config()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize secret client
        self._secret_client = self._initialize_keyvault_client()
        
        # Cache for secrets
        self._secrets_cache: Dict[str, str] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use default.
        
        Returns:
            Loaded configuration dictionary
        """
        try:
            # Try to load from specified path
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Could not load config from {self.config_path}: {e}")
        
        # Return default configuration if loading fails
        return self.DEFAULT_CONFIG

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration.
        
        Returns:
            Current configuration dictionary
        """
        return self.config

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

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._secrets_cache.clear()
