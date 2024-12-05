import os
from typing import Any, Dict, Optional
from functools import lru_cache
import json
from pathlib import Path

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

class ConfigurationManager:
    """Manages configuration and secrets for the logging framework."""
    
    def __init__(self, env_path: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            env_path: Optional path to .env file. If not provided, looks in current directory.
        """
        # Load environment variables
        load_dotenv(env_path)
        
        # Initialize Key Vault client
        self._secret_client = self._initialize_keyvault_client()
        
        # Cache for secrets
        self._secrets_cache: Dict[str, str] = {}

    def _initialize_keyvault_client(self) -> SecretClient:
        """Initialize Azure Key Vault client using credentials from environment."""
        required_vars = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'AZURE_KEYVAULT_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        credential = ClientSecretCredential(
            tenant_id=os.getenv('AZURE_TENANT_ID'),
            client_id=os.getenv('AZURE_CLIENT_ID'),
            client_secret=os.getenv('AZURE_CLIENT_SECRET')
        )
        
        return SecretClient(
            vault_url=os.getenv('AZURE_KEYVAULT_URL'),
            credential=credential
        )

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret from Azure Key Vault with caching.
        
        Args:
            secret_name: Name of the secret in Key Vault
            default: Default value if secret is not found
            
        Returns:
            The secret value or default if not found
        """
        try:
            if secret_name not in self._secrets_cache:
                secret = self._secret_client.get_secret(secret_name)
                self._secrets_cache[secret_name] = secret.value
            return self._secrets_cache[secret_name]
        except Exception as e:
            if default is not None:
                return default
            raise KeyError(f"Failed to retrieve secret '{secret_name}': {str(e)}")

    def process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process configuration dictionary and replace Key Vault references.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Processed configuration with resolved secrets
        """
        def process_value(value: Any) -> Any:
            if isinstance(value, str) and value.startswith('${kv:') and value.endswith('}'):
                # Extract secret name from ${kv:secret_name} format
                secret_name = value[4:-1]
                return self.get_secret(secret_name)
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(v) for v in value]
            return value

        return process_value(config)

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load and process configuration file.
        
        Args:
            config_path: Path to configuration file. If not provided, uses default path.
            
        Returns:
            Processed configuration dictionary
        """
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__),
                'skyarclog_logging.json'
            )

        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return self.process_config(config)

    def refresh_secrets(self) -> None:
        """Refresh all cached secrets from Key Vault."""
        self._secrets_cache.clear()
        get_secret.cache_clear()

    def get_connection_string(self, service_name: str) -> str:
        """Get a connection string for a specific service.
        
        Args:
            service_name: Name of the service (e.g., 'blob', 'sql', 'appinsights')
            
        Returns:
            Connection string for the service
        """
        secret_name = f"{service_name.upper()}-CONNECTION-STRING"
        return self.get_secret(secret_name)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._secrets_cache.clear()
