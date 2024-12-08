"""Configuration manager for SkyArcLog."""

import json
import os
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
        
        load_dotenv()
        self._secret_client = self._initialize_keyvault_client()
        
        # Cache for secrets
        self._secrets_cache: Dict[str, str] = {}

    def _initialize_keyvault_client(self) -> Optional[SecretClient]:
        """Initialize Azure Key Vault client using credentials from environment."""
        if not AZURE_AVAILABLE:
            return None
        
        required_vars = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'AZURE_KEYVAULT_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return None

        try:
            credentials = ClientSecretCredential(
                tenant_id=os.getenv('AZURE_TENANT_ID'),
                client_id=os.getenv('AZURE_CLIENT_ID'),
                client_secret=os.getenv('AZURE_CLIENT_SECRET')
            )
            
            return SecretClient(
                vault_url=os.getenv('AZURE_KEYVAULT_URL'),
                credential=credentials
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Key Vault client: {str(e)}")
            return None

    def get_secret(self, secret_name: str, default: Any = None) -> Any:
        """Get a secret from Azure Key Vault.
        
        Args:
            secret_name: Name of the secret
            default: Default value if secret is not found
            
        Returns:
            The secret value or default if not found
        """
        if not AZURE_AVAILABLE or not self._secret_client:
            return default
        
        try:
            if secret_name not in self._secrets_cache:
                secret = self._secret_client.get_secret(secret_name)
                self._secrets_cache[secret_name] = secret.value
            return self._secrets_cache[secret_name]
        except Exception as e:
            print(f"Warning: Failed to get secret {secret_name}: {str(e)}")
            return default

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

    def get_config(self) -> Dict[str, Any]:
        """Get the loaded configuration.
        
        Returns:
            Processed configuration dictionary
        """
        return self.load_config()

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
