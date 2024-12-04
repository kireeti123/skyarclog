"""
Listeners package for advanced logging framework.
"""

from .base import BaseListener
from .console import ConsoleListener
from .file import FileListener
from .sqlite import SQLiteListener
from .mysql import MySQLListener
from .postgresql import PostgreSQLListener
from .mssql import MSSQLListener
from .azure import AzureListener
from .azure_blob import AzureBlobListener

# Map of listener names to their classes
AVAILABLE_LISTENERS = {
    'console': ConsoleListener,
    'file': FileListener,
    'sqlite': SQLiteListener,
    'mysql': MySQLListener,
    'postgresql': PostgreSQLListener,
    'mssql': MSSQLListener,
    'azure': AzureListener,
    'azure_blob': AzureBlobListener,
}

__all__ = [
    'BaseListener',
    'ConsoleListener',
    'FileListener',
    'SQLiteListener',
    'MySQLListener',
    'PostgreSQLListener',
    'MSSQLListener',
    'AzureListener',
    'AzureBlobListener',
    'AVAILABLE_LISTENERS'
]
