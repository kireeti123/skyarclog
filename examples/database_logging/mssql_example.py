"""
MSSQL logging example.
"""

import os
from skyarclog import LogManager
from skyarclog.formatters import JSONFormatter
from skyarclog.listeners import MSSQLListener

# Initialize the log manager
log_manager = LogManager.get_instance()

# Add JSON formatter
log_manager.add_formatter(JSONFormatter())

# Add MSSQL listener
mssql_listener = MSSQLListener(
    server="localhost",
    database="logs_db",
    username="your_username",
    password="your_password",
    table_name="application_logs",
    batch_size=100,
    pool_size=5
)
log_manager.add_listener(mssql_listener)

# Log some messages
log_manager.info("Application started", source="example")
log_manager.error(
    "Database connection failed",
    source="database",
    extra={
        "error_code": 500,
        "connection_id": "12345"
    }
)

# Make sure to flush and close connections when done
log_manager.close()
