"""Azure SQL Database handler for logging."""

import logging
from typing import Optional, Dict, Any

from .utils import parse_connection_config
from .base_handler import AzureBaseHandler


class AzureSQLHandler(AzureBaseHandler):
    """Handler for logging to Azure SQL Database."""

    def __init__(
        self,
        connection_string: str,
        table_name: str,
        container_name: str = 'logs',
        blob_name_prefix: str = 'app_log',
        include_timestamp: bool = True,
        encoding: str = 'utf-8'
    ):
        """Initialize the handler.
        
        Args:
            connection_string: Azure SQL Database connection string
            table_name: Name of the SQL table
            container_name: Blob container name
            blob_name_prefix: Prefix for blob names
            include_timestamp: Whether to include timestamp in blob names
            encoding: Character encoding for log messages
        """
        super().__init__(container_name, blob_name_prefix, include_timestamp, encoding)
        self.connection_string = connection_string
        self.table_name = table_name

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record to Azure SQL Database.
        
        Args:
            record: Log record to emit
        """
        try:
            # Here you would insert the record into the SQL table using self.connection_string
            pass  # Implement SQL insertion logic here
        except Exception:
            self.handleError(record)

    @classmethod
    def create_handler(cls, config: Dict[str, Any]) -> Optional[logging.Handler]:
        """Create an Azure SQL Database handler from configuration.
        
        Args:
            config: Handler configuration
            
        Returns:
            Optional[logging.Handler]: Configured handler or None if creation fails
        """
        try:
            connection_string = config.get('connection_string')
            table_name = config.get('table_name')
            if not connection_string or not table_name:
                raise ValueError("Connection string and table name are required")
            
            return cls(
                connection_string=connection_string,
                table_name=table_name,
                container_name=config.get('container_name', 'logs'),
                blob_name_prefix=config.get('blob_name_prefix', 'app_log'),
                include_timestamp=config.get('include_timestamp', True),
                encoding=config.get('encoding', 'utf-8')
            )
        except Exception as e:
            logging.error(f"Failed to create Azure SQL handler: {str(e)}")
            return None
