"""Azure-specific logging handlers for skyarclog."""

from skyarclog.handlers.azure.blob_handler import create_blob_handler
from skyarclog.handlers.azure.appinsights_handler import create_appinsights_handler
from skyarclog.handlers.azure.sql_handler import create_sql_handler

__all__ = [
    'create_blob_handler',
    'create_appinsights_handler',
    'create_sql_handler'
]
