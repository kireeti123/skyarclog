"""
Microsoft SQL Server listener implementation using SQLAlchemy.
"""

from typing import Any, Dict, Optional
from sqlalchemy import BigInteger
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from ..formatters import BaseFormatter
from .sqlalchemy_base import SQLAlchemyBaseListener
import json
from datetime import datetime


class MSSQLListener(SQLAlchemyBaseListener):
    """
    Microsoft SQL Server listener implementation.
    Uses SQLAlchemy for database operations with connection pooling.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        formatter: Optional[BaseFormatter] = None
    ):
        """
        Initialize the MSSQL listener.
        
        Args:
            config: Listener configuration
            formatter: Optional log formatter
        """
        super().__init__(config, formatter)
        self.table_name = config.get("table_name", "application_logs")
        self.batch_size = config.get("batch_size", 100)
        self.log_buffer: list[dict[str, Any]] = []
        self.engine = create_engine(
            f"mssql+pymssql://{config['username']}:{config['password']}@{config['server']}/{config['database']}",
            pool_size=config.get("pool_size", 5),
            poolclass=StaticPool
        )
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the database table."""
        # Create initial connection
        with self.engine.connect() as conn:
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
            conn.execute(create_table_query)

    def get_primary_key_type(self):
        """Get the primary key column type for MSSQL."""
        return BigInteger

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

        with self.engine.connect() as conn:
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
                conn.execute(insert_query, batch_data)
                self.log_buffer.clear()

            except SQLAlchemyError as e:
                print(f"Error writing to MS SQL Server: {str(e)}")

    def close(self) -> None:
        """Close all database connections."""
        self.flush()  # Ensure all pending logs are written
        self.engine.dispose()
