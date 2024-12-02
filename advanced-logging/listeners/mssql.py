"""
Microsoft SQL Server Listener for SkyArcLog
Provides functionality to store logs in Microsoft SQL Server database
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pyodbc
from advanced_logging.listeners.base import BaseListener


class MSSQLListener(BaseListener):
    """
    Listener implementation for Microsoft SQL Server.
    Supports batch operations and connection pooling for optimal performance.
    """

    def __init__(
        self,
        server: str,
        database: str,
        username: str,
        password: str,
        driver: str = "ODBC Driver 17 for SQL Server",
        table_name: str = "application_logs",
        batch_size: int = 100,
        pool_size: int = 5,
    ):
        """
        Initialize the Microsoft SQL Server listener.

        Args:
            server (str): SQL Server hostname or IP
            database (str): Database name
            username (str): Database username
            password (str): Database password
            driver (str): ODBC Driver name (default: "ODBC Driver 17 for SQL Server")
            table_name (str): Name of the table to store logs (default: "application_logs")
            batch_size (int): Number of records to batch before writing (default: 100)
            pool_size (int): Size of the connection pool (default: 5)
        """
        super().__init__()
        self.connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        self.table_name = table_name
        self.batch_size = batch_size
        self.pool_size = pool_size
        self.log_buffer: List[Dict[str, Any]] = []
        self.connection_pool: List[pyodbc.Connection] = []
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the database table and connection pool."""
        # Create initial connection
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        create_table_query = f"""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[{self.table_name}]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [dbo].[{self.table_name}] (
                [id] [bigint] IDENTITY(1,1) PRIMARY KEY,
                [timestamp] [datetime2](7) NOT NULL,
                [level] [nvarchar](50) NOT NULL,
                [message] [nvarchar](max) NOT NULL,
                [logger] [nvarchar](255),
                [source] [nvarchar](255),
                [extra_data] [nvarchar](max),
                [created_at] [datetime2](7) DEFAULT GETUTCDATE()
            )

            CREATE INDEX [IX_{self.table_name}_timestamp] ON [dbo].[{self.table_name}] ([timestamp])
            CREATE INDEX [IX_{self.table_name}_level] ON [dbo].[{self.table_name}] ([level])
        END
        """
        cursor.execute(create_table_query)
        conn.commit()

        # Initialize connection pool
        self.connection_pool = [
            pyodbc.connect(self.connection_string) for _ in range(self.pool_size)
        ]

    def _get_connection(self) -> Tuple[pyodbc.Connection, int]:
        """Get a connection from the pool."""
        for i, conn in enumerate(self.connection_pool):
            try:
                if not conn.closed:
                    return conn, i
            except:
                # Replace dead connection
                self.connection_pool[i] = pyodbc.connect(self.connection_string)
                return self.connection_pool[i], i
        
        # If no connection is available, create a new one
        conn = pyodbc.connect(self.connection_string)
        self.connection_pool.append(conn)
        return conn, len(self.connection_pool) - 1

    def log(
        self,
        level: str,
        message: str,
        timestamp: Optional[datetime] = None,
        logger: Optional[str] = None,
        source: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log a message to Microsoft SQL Server.

        Args:
            level (str): Log level
            message (str): Log message
            timestamp (datetime, optional): Log timestamp
            logger (str, optional): Logger name
            source (str, optional): Log source
            **kwargs: Additional log data
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "logger": logger,
            "source": source,
            "extra_data": json.dumps(kwargs) if kwargs else None,
        }

        self.log_buffer.append(log_entry)

        if len(self.log_buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        """Flush buffered log entries to the database."""
        if not self.log_buffer:
            return

        conn, _ = self._get_connection()
        cursor = conn.cursor()

        try:
            # Prepare the insert query
            insert_query = f"""
            INSERT INTO [dbo].[{self.table_name}]
                ([timestamp], [level], [message], [logger], [source], [extra_data])
            VALUES
                (?, ?, ?, ?, ?, ?)
            """

            # Prepare batch data
            batch_data = [
                (
                    entry["timestamp"],
                    entry["level"],
                    entry["message"],
                    entry["logger"],
                    entry["source"],
                    entry["extra_data"],
                )
                for entry in self.log_buffer
            ]

            # Execute batch insert
            cursor.executemany(insert_query, batch_data)
            conn.commit()
            self.log_buffer.clear()

        except Exception as e:
            print(f"Error writing to MS SQL Server: {str(e)}")
            # Attempt to reconnect on next operation
            conn.close()
        finally:
            cursor.close()

    def close(self) -> None:
        """Close all database connections."""
        self.flush()  # Ensure all pending logs are written
        for conn in self.connection_pool:
            try:
                conn.close()
            except:
                pass
        self.connection_pool.clear()
