"""
MySQL listener for advanced logging framework.
"""

import json
from typing import Dict
try:
    import mysql.connector
except ImportError:
    print("MySQL listener requires mysql-connector-python package")

from .base import BaseListener

class MySQLListener(BaseListener):
    """
    Listener that logs to MySQL database
    """
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Initialize MySQL listener
        
        :param host: MySQL server host
        :param user: MySQL username
        :param password: MySQL password
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
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level VARCHAR(20),
                    message TEXT,
                    extra JSON
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"MySQL table creation error: {e}")

    def emit(self, log_entry: str):
        """
        Insert log entry into MySQL database
        
        :param log_entry: Formatted log entry
        """
        try:
            log_data = json.loads(log_entry)
            conn = mysql.connector.connect(**self.config)
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
            print(f"MySQL logging error: {e}")
