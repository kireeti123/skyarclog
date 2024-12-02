"""
PostgreSQL listener implementation using SQLAlchemy.
"""

import json
from typing import Dict, Any
try:
    import psycopg2
except ImportError:
    print("PostgreSQL listener requires psycopg2-binary package")

from sqlalchemy import BigInteger
from .sqlalchemy_base import SQLAlchemyBaseListener
from ..formatters import BaseFormatter

class PostgreSQLListener(SQLAlchemyBaseListener):
    """
    PostgreSQL listener implementation.
    Uses SQLAlchemy for database operations with connection pooling.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        formatter: BaseFormatter = None
    ):
        """
        Initialize the PostgreSQL listener.
        
        Args:
            config: Listener configuration
            formatter: Optional log formatter
        """
        super().__init__(config, formatter)
        
    def get_primary_key_type(self):
        """Get the primary key column type for PostgreSQL."""
        return BigInteger

    def _create_table(self):
        """
        Create logs table if not exists
        """
        try:
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level VARCHAR(20),
                    message TEXT,
                    extra JSONB
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"PostgreSQL table creation error: {e}")

    def emit(self, log_entry: str):
        """
        Insert log entry into PostgreSQL database
        
        :param log_entry: Formatted log entry
        """
        try:
            log_data = json.loads(log_entry)
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (level, message, extra) 
                VALUES (%s, %s, %s)
            ''', (
                log_data.get('level', ''),
                log_data.get('message', ''),
                json.dumps(log_data.get('extra', {}))
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"PostgreSQL logging error: {e}")
