"""Azure Blob Storage listener implementation."""

import json
import gzip
import os
from datetime import datetime
from typing import Any, Dict, List
from azure.storage.blob import BlobServiceClient
from ..buffered_listener import BufferedListener


class AzureBlobListener(BufferedListener):
    """Listener for Azure Blob Storage."""

    def __init__(self):
        """Initialize the Azure Blob Storage listener."""
        super().__init__()
        self._blob_service: BlobServiceClient = None
        self._container_name: str = None
        self._folder_structure: str = "{year}/{month}/{day}/{hour}"
        self._file_prefix: str = "app_log"
        self._file_extension: str = ".json"
        self._compress: bool = False
        self._min_size_for_compression: int = 10 * 1024 * 1024  # 10MB

    def initialize(self, name: str, config: Dict[str, Any]) -> None:
        """Initialize the listener with configuration.
        
        Args:
            name: Name of the listener instance
            config: Configuration dictionary containing:
                - container_connection_string: Azure Storage connection string
                - container_name: Blob container name
                - folder_structure: Format for folder structure (default: {year}/{month}/{day}/{hour})
                - file_prefix: Prefix for log files
                - file_extension: Extension for log files
                - compression: Compression settings
                - buffer: Buffer configuration (inherited from BufferedListener)
        """
        super().initialize(name, config)
        
        # Initialize blob service
        connection_string = config['container_connection_string']
        self._blob_service = BlobServiceClient.from_connection_string(connection_string)
        
        # Set container and path configuration
        self._container_name = config['container_name']
        self._folder_structure = config.get('folder_structure', self._folder_structure)
        self._file_prefix = config.get('file_prefix', self._file_prefix)
        self._file_extension = config.get('file_extension', self._file_extension)
        
        # Set compression configuration
        compression_config = config.get('compression', {})
        self._compress = compression_config.get('enabled', False)
        self._min_size_for_compression = compression_config.get('min_size', 10 * 1024 * 1024)

    def _handle_transformed_message(self, message: Dict[str, Any]) -> None:
        """Handle a transformed message.
        
        Args:
            message: Message to send to Blob Storage
        """
        # Not used - we handle messages in batches
        pass

    def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Send a batch of messages to Blob Storage.
        
        Args:
            batch: List of messages to send
        """
        if not batch:
            return

        # Generate blob path
        now = datetime.utcnow()
        folder = self._folder_structure.format(
            year=now.strftime('%Y'),
            month=now.strftime('%m'),
            day=now.strftime('%d'),
            hour=now.strftime('%H')
        )
        
        blob_name = f"{folder}/{self._file_prefix}_{now.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Convert messages to JSON
        content = "\n".join(json.dumps(msg) for msg in batch)
        
        # Compress if needed
        if self._compress and len(content.encode('utf-8')) >= self._min_size_for_compression:
            content = gzip.compress(content.encode('utf-8'))
            blob_name += ".gz"
        else:
            blob_name += self._file_extension
        
        # Upload to blob storage
        container_client = self._blob_service.get_container_client(self._container_name)
        blob_client = container_client.get_blob_client(blob_name)
        
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        blob_client.upload_blob(content, overwrite=True)

    def close(self) -> None:
        """Clean up resources."""
        super().close()
        if self._blob_service:
            self._blob_service.close()
