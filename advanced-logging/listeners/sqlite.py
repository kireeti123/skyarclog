"""
SQLite listener for advanced logging framework.
"""

import json
import sqlite3
from .base import BaseListener

class SQLiteListener(BaseListener):
    """
    Listener that logs to SQLite database
    """
    def __init__(self, db_path: str):
        """
        Initialize SQLite listener
        
        :param db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """
        Create logs table if not exists
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    extra TEXT
                )
            ''')
            conn.commit()

    def emit(self, log_entry: str):
        """
        Insert log entry into SQLite database
        
        :param log_entry: Formatted log entry
        """
        try:
            log_data = json.loads(log_entry)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs (level, message, extra) 
                    VALUES (?, ?, ?)
                ''', (
                    log_data.get('level', ''),
                    log_data.get('message', ''),
                    json.dumps(log_data.get('extra', {}))
                ))
                conn.commit()
        except Exception as e:
            print(f"SQLite logging error: {e}")
