"""
Key Vault manager for securely retrieving secrets.
Supports Azure Key Vault, AWS Secrets Manager, and Google Cloud Secret Manager.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# Azure Key Vault
try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# AWS Secrets Manager
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# Google Cloud Secret Manager
try:
    from google.cloud import secretmanager
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

class KeyVaultError(Exception):
    """Base exception for key vault operations."""
    pass

class KeyVaultProvider(ABC):
    """Abstract base class for key vault providers."""
    
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        """Retrieve a secret from the key vault."""
        pass

class AzureKeyVault(KeyVaultProvider):
    """Azure Key Vault implementation."""
    
    def __init__(self, vault_url: str):
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure Key Vault dependencies not installed. "
                "Install with: pip install azure-identity azure-keyvault-secrets"
            )
        
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=self.credential)
        
    def get_secret(self, secret_name: str) -> str:
        """Get secret from Azure Key Vault."""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            raise KeyVaultError(f"Failed to get secret from Azure Key Vault: {str(e)}")

class AWSSecretsManager(KeyVaultProvider):
    """AWS Secrets Manager implementation."""
    
    def __init__(self, region_name: str):
        if not AWS_AVAILABLE:
            raise ImportError(
                "AWS Secrets Manager dependencies not installed. "
                "Install with: pip install boto3"
            )
        
        self.client = boto3.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
    def get_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return response['SecretString']
            raise KeyVaultError("Secret value not found in response")
        except ClientError as e:
            raise KeyVaultError(f"Failed to get secret from AWS Secrets Manager: {str(e)}")

class GCPSecretManager(KeyVaultProvider):
    """Google Cloud Secret Manager implementation."""
    
    def __init__(self, project_id: str):
        if not GCP_AVAILABLE:
            raise ImportError(
                "Google Cloud Secret Manager dependencies not installed. "
                "Install with: pip install google-cloud-secret-manager"
            )
        
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id
        
    def get_secret(self, secret_name: str) -> str:
        """Get secret from Google Cloud Secret Manager."""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            raise KeyVaultError(
                f"Failed to get secret from Google Cloud Secret Manager: {str(e)}"
            )

class KeyVaultManager:
    """
    Unified interface for key vault operations across different cloud providers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize key vault manager based on configuration.
        
        Args:
            config: Configuration dictionary containing key vault settings
        """
        self.provider: Optional[KeyVaultProvider] = None
        self._initialize_provider(config)
        
    def _initialize_provider(self, config: Dict[str, Any]) -> None:
        """Initialize the appropriate key vault provider."""
        provider_type = config.get('provider', '').lower()
        
        if provider_type == 'azure':
            vault_url = config.get('vault_url')
            if not vault_url:
                raise KeyVaultError("Azure Key Vault URL not provided")
            self.provider = AzureKeyVault(vault_url)
            
        elif provider_type == 'aws':
            region = config.get('region')
            if not region:
                raise KeyVaultError("AWS region not provided")
            self.provider = AWSSecretsManager(region)
            
        elif provider_type == 'gcp':
            project_id = config.get('project_id')
            if not project_id:
                raise KeyVaultError("GCP project ID not provided")
            self.provider = GCPSecretManager(project_id)
            
        else:
            raise KeyVaultError(f"Unsupported key vault provider: {provider_type}")
        
    def get_connection_string(self, secret_name: str) -> str:
        """
        Get database connection string from key vault.
        
        Args:
            secret_name: Name of the secret containing the connection string
            
        Returns:
            str: Database connection string
            
        Raises:
            KeyVaultError: If secret retrieval fails
        """
        if not self.provider:
            raise KeyVaultError("Key vault provider not initialized")
        
        return self.provider.get_secret(secret_name)
