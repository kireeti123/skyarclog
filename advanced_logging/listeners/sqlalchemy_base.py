"""
SQLAlchemy base listener implementation for database logging.
"""

from typing import Any, Dict, List, Optional
import json
from datetime import datetime
import threading
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Index
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from ..formatters import BaseFormatter
from . import BaseListener
from ..security.key_vault import KeyVaultManager, KeyVaultError

class SQLAlchemyBaseListener(BaseListener):
    """
    Base listener implementation for SQLAlchemy-based database logging.
    Provides common functionality for database operations.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        formatter: Optional[BaseFormatter] = None
    ):
        """
        Initialize the SQLAlchemy listener.
        
        Args:
            config: Listener configuration
            formatter: Optional log formatter
        """
        super().__init__(config, formatter)
        
        self.table_name = config['table']
        self.schema = config.get('schema')
        self.batch_size = config.get('batch_size', 1000)
        self.create_table = config.get('create_table', True)
        self.indexes = config.get('indexes', [])
        
        self.engine: Optional[Engine] = None
        self.metadata = MetaData()
        self.table: Optional[Table] = None
        self._local = threading.local()
        
        # Initialize database connection
        self._initialize_database(config)
        
    def _get_connection_string(self, config: Dict[str, Any]) -> str:
        """Get database connection string from config or key vault."""
        # Check if key vault configuration is provided
        key_vault_config = config.get('key_vault')
        if key_vault_config:
            try:
                vault_manager = KeyVaultManager(key_vault_config)
                secret_name = key_vault_config.get('connection_string_secret')
                if not secret_name:
                    raise KeyVaultError(
                        "connection_string_secret not provided in key vault config"
                    )
                return vault_manager.get_connection_string(secret_name)
            except KeyVaultError as e:
                raise RuntimeError(f"Failed to get connection string from key vault: {str(e)}")
        
        # Fall back to direct configuration if no key vault is configured
        return config['sqlalchemy']['url']
        
    def _initialize_database(self, config: Dict[str, Any]) -> None:
        """Initialize database connection and create table if needed."""
        try:
            # Get connection string from key vault or config
            connection_string = self._get_connection_string(config)
            
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=config.get('pool_size', 5),
                max_overflow=config.get('max_overflow', 10),
                pool_timeout=config.get('pool_timeout', 30),
                pool_recycle=config.get('pool_recycle', 3600),
                echo=config.get('echo', False)
            )
            
            # Create table if it doesn't exist
            if self.create_table:
                self._create_table()
                
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {str(e)}")
            
    def _create_table(self) -> None:
        """Create the logging table if it doesn't exist."""
        self.table = Table(
            self.table_name,
            self.metadata,
            Column('id', self.get_primary_key_type(), primary_key=True),
            Column('timestamp', DateTime, nullable=False, index=True),
            Column('level', String(32), nullable=False, index=True),
            Column('logger_name', String(255), nullable=True, index=True),
            Column('message', String(4096), nullable=False),
            Column('extra', String(4096), nullable=True),
            schema=self.schema
        )
        
        # Create table and indexes
        if not self.table.exists(self.engine):
            self.metadata.create_all(self.engine)
            
            # Create additional indexes
            for index_column in self.indexes:
                if index_column not in ['timestamp', 'level', 'logger_name']:
                    Index(
                        f"ix_{self.table_name}_{index_column}",
                        self.table.c[index_column]
                    ).create(self.engine)
                    
    def get_primary_key_type(self):
        """Get the primary key column type. Override in subclasses."""
        raise NotImplementedError(
            "Subclasses must implement get_primary_key_type()"
        )
        
    def _get_connection(self):
        """Get a connection from the connection pool."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = self.engine.connect()
        return self._local.connection
        
    def _format_log_entry(self, message: str, level: str, extra: Dict) -> Dict:
        """Format a log entry for database insertion."""
        formatted = self.formatter.format(message, level, extra)
        if isinstance(formatted, str):
            formatted = json.loads(formatted)
            
        return {
            'timestamp': datetime.utcnow(),
            'level': level,
            'logger_name': extra.get('logger_name'),
            'message': message,
            'extra': json.dumps(extra) if extra else None
        }
        
    def emit(self, message: str, level: str, extra: Optional[Dict] = None) -> None:
        """
        Emit a log message to the database.
        
        Args:
            message: Log message
            level: Log level
            extra: Optional extra data
        """
        try:
            entry = self._format_log_entry(message, level, extra or {})
            
            with self._get_connection() as conn:
                conn.execute(
                    self.table.insert(),
                    entry
                )
                
        except SQLAlchemyError as e:
            print(f"Error writing to database: {str(e)}")
            
    def emit_batch(self, entries: List[Dict[str, Any]]) -> None:
        """
        Emit a batch of log messages to the database.
        
        Args:
            entries: List of log entries to insert
        """
        if not entries:
            return
            
        try:
            formatted_entries = [
                self._format_log_entry(
                    entry['message'],
                    entry['level'],
                    entry.get('extra', {})
                )
                for entry in entries
            ]
            
            with self._get_connection() as conn:
                conn.execute(
                    self.table.insert(),
                    formatted_entries
                )
                
        except SQLAlchemyError as e:
            print(f"Error writing batch to database: {str(e)}")
            
    def flush(self) -> None:
        """Flush any buffered log messages."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
            
    def close(self) -> None:
        """Close the database connection."""
        self.flush()
        if self.engine:
            self.engine.dispose()
            
    def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            with self._get_connection() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False
