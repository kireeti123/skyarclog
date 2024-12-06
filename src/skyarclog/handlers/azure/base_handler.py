"""Abstract base class for Azure logging handlers."""

import logging
from abc import ABC, abstractmethod


class AzureBaseHandler(logging.Handler, ABC):
    """Abstract base class for Azure logging handlers."""

    def __init__(self, container_name: str, blob_name_prefix: str, include_timestamp: bool, encoding: str):
        """Initialize the base handler.
        
        Args:
            container_name: Name of the Azure blob container
            blob_name_prefix: Prefix for blob names
            include_timestamp: Whether to include timestamp in blob names
            encoding: Character encoding for log messages
        """
        super().__init__()
        self.container_name = container_name
        self.blob_name_prefix = blob_name_prefix
        self.include_timestamp = include_timestamp
        self.encoding = encoding

    @abstractmethod
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Azure storage.
        
        Args:
            record: Log record to emit
        """
        pass

    @abstractmethod
    def create_handler(config: dict) -> logging.Handler:
        """Create an Azure handler from configuration.
        
        Args:
            config: Configuration dictionary for the handler
        
        Returns:
            logging.Handler: Configured Azure handler
        """
        pass

