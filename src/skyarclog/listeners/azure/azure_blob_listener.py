"""Azure Blob Storage listener implementation."""

from typing import Dict, Any
from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient
from ..base_listener import BaseListener

class AzureBlobListener(BaseListener):
    """Listener that writes log messages to Azure Blob Storage."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Azure Blob listener.
        
        Args:
            config: Listener configuration
        """
        super().__init__(config)
        self._blob_service = None
        self._container_name = self._config.get('container_name', 'logs')
        self._connection_string = self._config.get('connection_string')
        self._blob_prefix = self._config.get('blob_prefix', '')
        self._setup_blob_service()

    def _setup_blob_service(self) -> None:
        """Set up the blob service client."""
        if not self._connection_string:
            raise ValueError("Azure Blob connection string not provided")

        try:
            self._blob_service = BlobServiceClient.from_connection_string(
                self._connection_string
            )
            # Create container if it doesn't exist
            container_client = self._blob_service.get_container_client(
                self._container_name
            )
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Azure Blob Storage: {e}")

    def _get_blob_name(self, timestamp: datetime) -> str:
        """Generate a blob name based on timestamp.
        
        Args:
            timestamp: Message timestamp
            
        Returns:
            Blob name
        """
        date_str = timestamp.strftime('%Y/%m/%d/%H_%M_%S_%f')
        return f"{self._blob_prefix}/{date_str}.json"

    def emit(self, message: Dict[str, Any]) -> None:
        """Write the message to Azure Blob Storage.
        
        Args:
            message: Message to write
        """
        if not self._blob_service:
            return

        try:
            formatted_message = self.format_message(message)
            timestamp = datetime.now()
            blob_name = self._get_blob_name(timestamp)
            
            # Add timestamp to message
            formatted_message['timestamp'] = timestamp.isoformat()
            
            # Convert message to JSON
            message_json = json.dumps(formatted_message, indent=2)
            
            # Upload to blob storage
            blob_client = self._blob_service.get_blob_client(
                container=self._container_name,
                blob=blob_name
            )
            blob_client.upload_blob(message_json, overwrite=True)
        except Exception as e:
            raise RuntimeError(f"Failed to write message to Azure Blob Storage: {e}")

    def close(self) -> None:
        """Close the blob service client."""
        if self._blob_service:
            self._blob_service.close()
