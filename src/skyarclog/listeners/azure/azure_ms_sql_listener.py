"""Azure MS SQL Server listener implementation."""

from typing import Dict, Any
import pyodbc
from ..base_listener import BaseListener

class AzureMsSqlListener(BaseListener):
    """Listener that writes log messages to Azure SQL Database."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Azure MS SQL listener.
        
        Args:
            config: Listener configuration
        """
        super().__init__(config)
        self._connection = None
        self._table_name = self._config.get('table_name', 'ApplicationLogs')
        self._schema_name = self._config.get('schema_name', 'dbo')
        self._setup_connection()

    def _setup_connection(self) -> None:
        """Set up the database connection."""
        connection_string = self._config.get('connection_string')
        if not connection_string:
            raise ValueError("Azure MS SQL connection string not provided")

        try:
            self._connection = pyodbc.connect(connection_string)
            self._create_table_if_not_exists()
        except pyodbc.Error as e:
            raise RuntimeError(f"Failed to connect to Azure MS SQL: {e}")

    def _create_table_if_not_exists(self) -> None:
        """Create the logging table if it doesn't exist."""
        create_table_sql = f"""
        IF NOT EXISTS (
            SELECT * FROM sys.objects 
            WHERE object_id = OBJECT_ID(N'[{self._schema_name}].[{self._table_name}]') 
            AND type in (N'U')
        )
        BEGIN
            CREATE TABLE [{self._schema_name}].[{self._table_name}] (
                Id BIGINT IDENTITY(1,1) PRIMARY KEY,
                Timestamp DATETIME2 NOT NULL,
                Level NVARCHAR(50) NOT NULL,
                Message NVARCHAR(MAX) NOT NULL,
                Context NVARCHAR(MAX)
            )
        END
        """
        
        with self._connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            self._connection.commit()

    def emit(self, message: Dict[str, Any]) -> None:
        """Write the message to Azure SQL Database.
        
        Args:
            message: Message to write
        """
        if not self._connection:
            return

        formatted_message = self.format_message(message)
        
        insert_sql = f"""
        INSERT INTO [{self._schema_name}].[{self._table_name}]
        (Timestamp, Level, Message, Context)
        VALUES (GETDATE(), ?, ?, ?)
        """
        
        with self._connection.cursor() as cursor:
            cursor.execute(
                insert_sql,
                formatted_message.get('level', 'INFO'),
                str(formatted_message.get('message', '')),
                str(formatted_message.get('context', {}))
            )
            self._connection.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
