"""
Azure Blob Storage listener for logging.
"""

import os
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
from ..formatters import BaseFormatter
from . import BaseListener
from ..security.key_vault import KeyVaultManager

class AzureBlobListener(BaseListener):
    """
    Azure Blob Storage listener implementation.
    Supports structured logging with automatic container management.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        formatter: Optional[BaseFormatter] = None
    ):
        """
        Initialize Azure Blob Storage listener.
        
        Args:
            config: Listener configuration containing Blob Storage settings
            formatter: Optional log formatter
        """
        super().__init__(config, formatter)
        
        # Get connection string from key vault
        self.connection_string = self._get_connection_string(config)
        
        # Get container configuration
        self.container_name = config.get('container_name', 'application-logs')
        self.folder_structure = config.get(
            'folder_structure',
            '{year}/{month}/{day}'
        )
        self.file_prefix = config.get('file_prefix', 'log')
        self.file_extension = config.get('file_extension', '.json')
        self.max_file_size = config.get('max_file_size_mb', 100) * 1024 * 1024
        
        # Initialize blob client
        self._init_blob_client()
        
        # Current file tracking
        self._current_blob_name = None
        self._current_size = 0
        
    def _get_connection_string(self, config: Dict[str, Any]) -> str:
        """Get Blob Storage connection string from key vault."""
        secret_name = config.get('connection_string_secret')
        if not secret_name:
            raise RuntimeError(
                "connection_string_secret not provided in config"
            )
            
        key_vault_config = config.get('key_vault', {})
        if not key_vault_config:
            raise RuntimeError("Key vault configuration not found")
            
        try:
            vault_manager = KeyVaultManager(key_vault_config)
            return vault_manager.get_secret(secret_name)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get Blob Storage connection string: {str(e)}"
            )
            
    def _init_blob_client(self) -> None:
        """Initialize Blob Service client and create container if needed."""
        try:
            self.blob_service = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            
            # Create container if it doesn't exist
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            if not container_client.exists():
                container_client.create_container()
                
        except AzureError as e:
            raise RuntimeError(f"Failed to initialize blob client: {str(e)}")
            
    def _get_blob_name(self) -> str:
        """Generate blob name based on current time and configuration."""
        now = datetime.now()
        
        # Create folder structure
        folder = self.folder_structure.format(
            year=now.strftime('%Y'),
            month=now.strftime('%m'),
            day=now.strftime('%d')
        )
        
        # Generate unique file name
        timestamp = now.strftime('%H%M%S')
        unique_id = str(int(time.time() * 1000))[-6:]  # Last 6 digits
        
        return f"{folder}/{self.file_prefix}_{timestamp}_{unique_id}{self.file_extension}"
        
    def _should_rotate_file(self) -> bool:
        """Check if we should start a new blob file."""
        return (
            self._current_blob_name is None or
            self._current_size >= self.max_file_size
        )
        
    def _write_to_blob(
        self,
        blob_name: str,
        content: str,
        append: bool = True
    ) -> None:
        """Write content to blob."""
        try:
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            if append and blob_client.exists():
                # Download existing content
                existing_content = blob_client.download_blob().readall()
                content = existing_content.decode() + '\n' + content
                
            # Upload content
            blob_client.upload_blob(
                content.encode(),
                overwrite=True
            )
            
            # Update tracking
            self._current_blob_name = blob_name
            self._current_size = len(content.encode())
            
        except AzureError as e:
            raise RuntimeError(f"Failed to write to blob: {str(e)}")
            
    def emit(self, message: str, level: str, extra: Optional[Dict] = None) -> None:
        """
        Emit a log message to Azure Blob Storage.
        
        Args:
            message: Log message
            level: Log level
            extra: Optional extra data
        """
        try:
            # Format the log message
            formatted = self.formatter.format(message, level, extra or {})
            
            # Check if we need to rotate file
            if self._should_rotate_file():
                self._current_blob_name = self._get_blob_name()
                self._current_size = 0
                
            # Write to blob
            self._write_to_blob(
                self._current_blob_name,
                formatted,
                append=True
            )
            
        except Exception as e:
            print(f"Error writing to Azure Blob Storage: {str(e)}")
            
    def flush(self) -> None:
        """Flush is not needed for blob storage."""
        pass
        
    def close(self) -> None:
        """Close blob service client."""
        try:
            self.blob_service.close()
        except Exception as e:
            print(f"Error closing Azure Blob Storage client: {str(e)}")
            
    def health_check(self) -> bool:
        """
        Check if Azure Blob Storage connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            # Try to list blobs
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            next(container_client.list_blobs(max_results=1), None)
            return True
        except:
            return False
