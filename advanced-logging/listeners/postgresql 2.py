"""
PostgreSQL listener for advanced logging framework.
"""

import json
from typing import Dict
try:
    import psycopg2
except ImportError:
    print("PostgreSQL listener requires psycopg2-binary package")

from .base import BaseListener

class PostgreSQLListener(BaseListener):
    """
    Listener that logs to PostgreSQL database
    """
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Initialize PostgreSQL listener
        
        :param host: PostgreSQL server host
        :param user: PostgreSQL username
        :param password: PostgreSQL password
        :param database: Database name
        """
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self._create_table()

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
