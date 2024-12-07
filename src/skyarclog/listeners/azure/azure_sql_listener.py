"""Azure SQL Database listener implementation."""

import json
from datetime import datetime
from typing import Any, Dict, List
import pyodbc
from ..buffered_listener import BufferedListener


class AzureSqlListener(BufferedListener):
    """Listener for Azure SQL Database."""

    def __init__(self):
        """Initialize the Azure SQL Database listener."""
        super().__init__()
        self._connection = None
        self._table_name = "ApplicationLogs"
        self._schema = "dbo"
        self._connection_string = None
        self._auto_create_table = True
        self._batch_size = 100

    def initialize(self, name: str, config: Dict[str, Any]) -> None:
        """Initialize the listener with configuration.
        
        Args:
            name: Name of the listener instance
            config: Configuration dictionary containing:
                - connection_string: SQL Server connection string
                - table_name: Target table name (default: ApplicationLogs)
                - schema: Database schema (default: dbo)
                - auto_create_table: Whether to create table if not exists
                - buffer: Buffer configuration (inherited from BufferedListener)
        """
        super().initialize(name, config)
        
        # Set configuration
        self._connection_string = config['connection_string']
        self._table_name = config.get('table_name', self._table_name)
        self._schema = config.get('schema', self._schema)
        self._auto_create_table = config.get('auto_create_table', True)
        
        # Initialize database connection
        self._setup_database()

    def _setup_database(self) -> None:
        """Set up database connection and create table if needed."""
        self._connection = pyodbc.connect(self._connection_string)
        
        if self._auto_create_table:
            self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        """Create the log table if it doesn't exist."""
        create_table_sql = f"""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[{self._schema}].[{self._table_name}]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [{self._schema}].[{self._table_name}] (
                [Id] [bigint] IDENTITY(1,1) NOT NULL PRIMARY KEY,
                [Timestamp] [datetime2](7) NOT NULL,
                [Level] [nvarchar](50) NOT NULL,
                [Message] [nvarchar](max) NULL,
                [Properties] [nvarchar](max) NULL,
                [Exception] [nvarchar](max) NULL,
                [ApplicationName] [nvarchar](255) NULL,
                [Environment] [nvarchar](50) NULL,
                [CorrelationId] [nvarchar](100) NULL,
                [CustomDimensions] [nvarchar](max) NULL
            )
            
            CREATE NONCLUSTERED INDEX [IX_{self._table_name}_Timestamp] ON [{self._schema}].[{self._table_name}]
            (
                [Timestamp] ASC
            )
            
            CREATE NONCLUSTERED INDEX [IX_{self._table_name}_Level] ON [{self._schema}].[{self._table_name}]
            (
                [Level] ASC
            )
        END
        """
        
        with self._connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            self._connection.commit()

    def _handle_transformed_message(self, message: Dict[str, Any]) -> None:
        """Handle a transformed message.
        
        Args:
            message: Message to write to SQL Server
        """
        # Not used - we handle messages in batches
        pass

    def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Send a batch of messages to SQL Server.
        
        Args:
            batch: List of messages to send
        """
        if not batch:
            return

        # Prepare insert statement
        insert_sql = f"""
        INSERT INTO [{self._schema}].[{self._table_name}]
        (Timestamp, Level, Message, Properties, Exception, ApplicationName, Environment, CorrelationId, CustomDimensions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare batch values
        values = []
        for msg in batch:
            # Extract common fields
            timestamp = msg.get('timestamp', datetime.utcnow())
            level = msg.get('level', 'INFO')
            message = msg.get('message', '')
            
            # Extract special fields
            exception = msg.pop('exception', None)
            app_name = msg.pop('application_name', None)
            environment = msg.pop('environment', None)
            correlation_id = msg.pop('correlation_id', None)
            
            # Remove standard fields from custom dimensions
            for field in ['timestamp', 'level', 'message']:
                msg.pop(field, None)
            
            # Convert remaining fields to JSON
            properties = json.dumps(msg) if msg else None
            
            values.append((
                timestamp,
                level,
                message,
                properties,
                exception,
                app_name,
                environment,
                correlation_id,
                properties  # Store all custom fields in CustomDimensions as well
            ))
        
        # Execute batch insert
        with self._connection.cursor() as cursor:
            cursor.fast_executemany = True
            cursor.executemany(insert_sql, values)
            self._connection.commit()

    def close(self) -> None:
        """Clean up resources."""
        super().close()
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass  # Ignore errors during cleanup
