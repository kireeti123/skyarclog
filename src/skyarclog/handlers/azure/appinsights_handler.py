"""Azure Application Insights handler for logging."""

import logging
from typing import Optional, Dict, Any

from opencensus.ext.azure.log_exporter import AzureLogHandler

from .utils import parse_connection_config
from .base_handler import AzureBaseHandler


class AzureAppInsightsHandler(AzureBaseHandler):
    """Handler for logging to Azure Application Insights."""

    def __init__(
        self,
        instrumentation_key: str,
        container_name: str = 'logs',
        blob_name_prefix: str = 'app_log',
        include_timestamp: bool = True,
        encoding: str = 'utf-8'
    ):
        """Initialize the handler.
        
        Args:
            instrumentation_key: Azure Application Insights instrumentation key
            container_name: Blob container name
            blob_name_prefix: Prefix for blob names
            include_timestamp: Whether to include timestamp in blob names
            encoding: Character encoding for log messages
        """
        super().__init__(container_name, blob_name_prefix, include_timestamp, encoding)
        
        self.handler = AzureLogHandler(connection_string=instrumentation_key)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record to Azure Application Insights.
        
        Args:
            record: Log record to emit
        """
        try:
            self.handler.emit(record)
        except Exception:
            self.handleError(record)

    @classmethod
    def create_handler(cls, config: Dict[str, Any]) -> Optional[logging.Handler]:
        """Create an Azure Application Insights handler from configuration.
        
        Args:
            config: Handler configuration
            
        Returns:
            Optional[logging.Handler]: Configured handler or None if creation fails
        """
        try:
            # Parse connection configuration
            instrumentation_key = config.get('instrumentation_key')
            if not instrumentation_key:
                raise ValueError("Instrumentation key is required")
            
            # Create handler
            return cls(
                instrumentation_key=instrumentation_key,
                container_name=config.get('container_name', 'logs'),
                blob_name_prefix=config.get('blob_name_prefix', 'app_log'),
                include_timestamp=config.get('include_timestamp', True),
                encoding=config.get('encoding', 'utf-8')
            )
        except Exception as e:
            logging.error(f"Failed to create Azure App Insights handler: {str(e)}")
            return None
