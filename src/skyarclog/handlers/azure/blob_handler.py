"""Azure Blob Storage handler for logging."""

import json
import logging
from typing import Optional, Dict, Any

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

from .utils import (
    create_blob_service_client,
    parse_connection_config,
    format_blob_name,
    format_log_record,
    AzureConnectionError
)
from .base_handler import AzureBaseHandler


class AzureBlobHandler(AzureBaseHandler):
    """Handler for logging to Azure Blob Storage."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_url: Optional[str] = None,
        credential: Optional[Any] = None,
        container_name: str = 'logs',
        blob_name_prefix: str = 'app_log',
        include_timestamp: bool = True,
        encoding: str = 'utf-8'
    ):
        """Initialize the handler.
        
        Args:
            connection_string: Azure Storage connection string
            account_url: Azure Storage account URL
            credential: Azure credential object
            container_name: Blob container name
            blob_name_prefix: Prefix for blob names
            include_timestamp: Whether to include timestamp in blob names
            encoding: Character encoding for log messages
            
        Raises:
            AzureConnectionError: If connection to Azure fails
        """
        super().__init__(container_name, blob_name_prefix, include_timestamp, encoding)
        
        # Initialize blob service client
        self.blob_service_client = create_blob_service_client(
            connection_string, account_url, credential
        )
        
        # Create container if it doesn't exist
        self._ensure_container_exists()

    def _ensure_container_exists(self) -> None:
        """Ensure that the Azure blob container exists."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
        except AzureError as e:
            raise AzureConnectionError(f"Failed to create/access container: {str(e)}")

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record to Azure Blob Storage.
        
        Args:
            record: Log record to emit
        """
        try:
            # Format the record
            formatted_record = format_log_record(record)
            
            # Generate blob name
            blob_name = format_blob_name(
                self.blob_name_prefix,
                extension='.json',
                include_timestamp=self.include_timestamp
            )
            
            # Upload to blob storage
            blob_client = self.blob_service_client.get_container_client(
                self.container_name
            ).get_blob_client(blob_name)
            
            blob_client.upload_blob(
                json.dumps(formatted_record, ensure_ascii=False).encode(self.encoding),
                overwrite=True
            )
        except Exception:
            self.handleError(record)

    @classmethod
    def create_handler(cls, config: Dict[str, Any]) -> Optional[logging.Handler]:
        """Create an Azure Blob Storage handler from configuration.
        
        Args:
            config: Handler configuration
            
        Returns:
            Optional[logging.Handler]: Configured handler or None if creation fails
        """
        try:
            # Parse connection configuration
            connection_string, account_url, credential = parse_connection_config(config)
            
            # Create handler
            return cls(
                connection_string=connection_string,
                account_url=account_url,
                credential=credential,
                container_name=config.get('container_name', 'logs'),
                blob_name_prefix=config.get('blob_name_prefix', 'app_log'),
                include_timestamp=config.get('include_timestamp', True),
                encoding=config.get('encoding', 'utf-8')
            )
        except Exception as e:
            logging.error(f"Failed to create Azure Blob handler: {str(e)}")
            return None
