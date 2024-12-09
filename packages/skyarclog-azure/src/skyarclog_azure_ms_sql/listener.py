"""Azure MS SQL listener for SkyArcLog."""

import pyodbc
from typing import Any, Dict
from skyarclog.listeners.base import BaseListener
from .formatter import SqlFormatter

class AzureMsSqlListener(BaseListener):
    """Azure MS SQL listener for SkyArcLog."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Azure MS SQL listener.
        
        Args:
            config: Configuration dictionary containing:
                - connection_string: SQL Server connection string
                - table_name: Target table name
                - batch_size: Optional batch size for inserts
                - flush_interval: Optional flush interval in seconds
        """
        super().__init__(config)
        self.connection_string = config.get('connection_string')
        self.table_name = config.get('table_name')
        self.batch_size = config.get('batch_size', 100)
        self.flush_interval = config.get('flush_interval', 30)
        self.connection = None
        self.cursor = None
        self.buffer = []
        
        # Initialize SQL formatter
        formatter_config = config.get('formatter_config', {})
        self.formatter = SqlFormatter(formatter_config)
        
    def initialize(self):
        """Initialize the SQL Server connection."""
        self.connection = pyodbc.connect(self.connection_string)
        self.cursor = self.connection.cursor()
        
    def emit(self, record: Dict[str, Any]):
        """Emit a log record to Azure MS SQL.
        
        Args:
            record: Log record to emit
        """
        if not self.connection or not self.cursor:
            self.initialize()
            
        # Format the record as a SQL statement using our formatter
        sql = self.formatter.format(record).format(table_name=self.table_name)
        
        # Execute the SQL statement
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            # If there's an error, try to reconnect once
            self.close()
            self.initialize()
            self.cursor.execute(sql)
            self.connection.commit()
        
    def close(self):
        """Close the SQL Server connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
