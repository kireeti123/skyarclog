"""
MySQL listener for advanced logging framework with connection pooling support.
"""

import json
import threading
from typing import Dict, Optional, Union
try:
    import pymysql
    from pymysql.cursors import DictCursor
    from dbutils.pooled_db import PooledDB
except ImportError:
    print("MySQL listener requires PyMySQL and DBUtils packages")

from .base import BaseListener

class MySQLListener(BaseListener):
    """
    Listener that logs to MySQL database using PyMySQL with connection pooling
    """
    _pool = None
    _pool_lock = threading.Lock()

    def __init__(self, 
                 host: str, 
                 user: str, 
                 password: str, 
                 database: str,
                 port: int = 3306,
                 charset: str = 'utf8mb4',
                 table_name: str = 'logs',
                 min_connections: int = 1,
                 max_connections: int = 10,
                 connection_timeout: int = 30,
                 ping_interval: int = 300):
        """
        Initialize MySQL listener with connection pooling
        
        :param host: MySQL server host
        :param user: MySQL username
        :param password: MySQL password
        :param database: Database name
        :param port: MySQL port (default: 3306)
        :param charset: Character set (default: utf8mb4)
        :param table_name: Log table name (default: logs)
        :param min_connections: Minimum connections in pool (default: 1)
        :param max_connections: Maximum connections in pool (default: 10)
        :param connection_timeout: Connection timeout in seconds (default: 30)
        :param ping_interval: Database ping interval in seconds (default: 300)
        """
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': charset,
            'cursorclass': DictCursor
        }
        self.pool_config = {
            'mincached': min_connections,
            'maxcached': max_connections,
            'maxconnections': max_connections,
            'blocking': True,
            'ping': ping_interval,
            'timeout': connection_timeout
        }
        self.table_name = table_name
        self._initialize_pool()
        self._create_table()

    def _initialize_pool(self):
        """
        Initialize the connection pool if not already initialized
        """
        if MySQLListener._pool is None:
            with MySQLListener._pool_lock:
                if MySQLListener._pool is None:  # Double-check pattern
                    try:
                        MySQLListener._pool = PooledDB(
                            creator=pymysql,
                            **self.pool_config,
                            **self.db_config
                        )
                    except Exception as e:
                        print(f"Failed to initialize connection pool: {e}")
                        raise

    def _get_connection(self):
        """
        Get a connection from the pool with health check
        
        :return: MySQL connection from pool
        """
        try:
            conn = MySQLListener._pool.connection()
            # Test connection with a simple query
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return conn
        except Exception as e:
            print(f"Failed to get connection from pool: {e}")
            # Try to reinitialize the pool
            self._initialize_pool()
            raise

    def _create_table(self):
        """
        Create logs table if not exists with improved schema and partitioning
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create the table with partitioning by timestamp
                    cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.table_name} (
                            id BIGINT AUTO_INCREMENT PRIMARY KEY,
                            timestamp TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
                            level VARCHAR(20) NOT NULL,
                            message TEXT NOT NULL,
                            logger_name VARCHAR(100),
                            source_file VARCHAR(255),
                            source_line INT,
                            function_name VARCHAR(100),
                            thread_id VARCHAR(50),
                            process_id VARCHAR(50),
                            extra JSON,
                            INDEX idx_timestamp (timestamp),
                            INDEX idx_level (level),
                            INDEX idx_logger (logger_name)
                        ) ENGINE=InnoDB 
                        DEFAULT CHARSET=utf8mb4 
                        COLLATE=utf8mb4_unicode_ci
                        PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp)) (
                            PARTITION p_min VALUES LESS THAN (0),
                            PARTITION p_current VALUES LESS THAN (MAXVALUE)
                        )
                    ''')
                conn.commit()
        except Exception as e:
            print(f"MySQL table creation error: {e}")
            raise

    def emit(self, log_entry: Union[str, Dict]):
        """
        Insert log entry into MySQL database with improved error handling and retries
        
        :param log_entry: Formatted log entry (JSON string or dict)
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Parse log entry if it's a string
                log_data = json.loads(log_entry) if isinstance(log_entry, str) else log_entry
                
                # Extract fields with defaults
                extra = log_data.get('extra', {})
                source_info = extra.get('source', {})
                
                with self._get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(f'''
                            INSERT INTO {self.table_name} (
                                level, message, logger_name, source_file,
                                source_line, function_name, thread_id,
                                process_id, extra
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            log_data.get('level', 'NOTSET'),
                            log_data.get('message', ''),
                            log_data.get('logger_name', ''),
                            source_info.get('file', ''),
                            source_info.get('line', None),
                            source_info.get('function', ''),
                            str(extra.get('thread_id', '')),
                            str(extra.get('process_id', '')),
                            json.dumps(extra)
                        ))
                    conn.commit()
                break  # Success, exit retry loop
                
            except Exception as e:
                retry_count += 1
                print(f"MySQL logging error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    raise  # Re-raise the last exception after max retries

    def close(self):
        """
        Clean up resources and close the connection pool
        """
        if MySQLListener._pool is not None:
            try:
                MySQLListener._pool.close()
                MySQLListener._pool = None
            except Exception as e:
                print(f"Error closing connection pool: {e}")

    def __del__(self):
        """
        Ensure resources are cleaned up
        """
        self.close()
