"""Utility functions for Azure handlers."""

from typing import Optional, Dict, Any, Tuple
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError


class AzureConnectionError(Exception):
    """Exception raised for Azure connection errors."""
    pass


def create_blob_service_client(
    connection_string: Optional[str] = None,
    account_url: Optional[str] = None,
    credential: Optional[Any] = None
) -> BlobServiceClient:
    """Create a BlobServiceClient with the provided credentials.
    
    Args:
        connection_string: Azure Storage connection string
        account_url: Azure Storage account URL
        credential: Azure credential object
        
    Returns:
        BlobServiceClient: Initialized blob service client
        
    Raises:
        AzureConnectionError: If connection fails
    """
    try:
        if connection_string:
            return BlobServiceClient.from_connection_string(connection_string)
        elif account_url:
            credential = credential or DefaultAzureCredential()
            return BlobServiceClient(account_url, credential=credential)
        else:
            raise ValueError(
                "Either connection_string or account_url must be provided"
            )
    except AzureError as e:
        raise AzureConnectionError(f"Failed to create blob service client: {str(e)}")


def parse_connection_config(
    config: Dict[str, Any]
) -> Tuple[Optional[str], Optional[str], Optional[Any]]:
    """Parse Azure connection configuration.
    
    Args:
        config: Configuration dictionary containing connection details
        
    Returns:
        Tuple containing:
            - connection_string: Optional connection string
            - account_url: Optional account URL
            - credential: Optional credential object
    """
    connection_string = config.get('connection_string')
    account_url = config.get('account_url')
    credential = None

    if not connection_string and account_url:
        credential = (
            config.get('credential') or 
            DefaultAzureCredential(
                exclude_shared_token_cache_credential=True,
                exclude_visual_studio_code_credential=True
            )
        )

    return connection_string, account_url, credential


def format_blob_name(
    base_name: str,
    extension: str = '.json',
    include_timestamp: bool = True
) -> str:
    """Format blob name with optional timestamp.
    
    Args:
        base_name: Base name for the blob
        extension: File extension (default: '.json')
        include_timestamp: Whether to include timestamp in name
        
    Returns:
        str: Formatted blob name
    """
    from datetime import datetime
    
    if include_timestamp:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}{extension}"
    return f"{base_name}{extension}"


def create_table_if_not_exists(
    cursor: Any,
    table_name: str,
    schema: str = None
) -> None:
    """Create SQL table if it doesn't exist.
    
    Args:
        cursor: Database cursor
        table_name: Name of the table
        schema: Optional schema definition
        
    Raises:
        Exception: If table creation fails
    """
    if not schema:
        schema = """
        CREATE TABLE {table_name} (
            id INT IDENTITY(1,1) PRIMARY KEY,
            timestamp DATETIME2 DEFAULT GETUTCDATE(),
            level VARCHAR(50),
            logger_name VARCHAR(255),
            message NVARCHAR(MAX),
            exception NVARCHAR(MAX),
            extra_data NVARCHAR(MAX)
        )
        """.format(table_name=table_name)

    try:
        # Check if table exists
        cursor.execute(f"""
            IF NOT EXISTS (
                SELECT * FROM sys.tables 
                WHERE name = '{table_name}' AND type = 'U'
            )
            BEGIN
                {schema}
            END
        """)
        cursor.commit()
    except Exception as e:
        raise Exception(f"Failed to create table {table_name}: {str(e)}")


def format_log_record(record: Any) -> Dict[str, Any]:
    """Format log record for Azure storage.
    
    Args:
        record: Log record to format
        
    Returns:
        Dict: Formatted log record
    """
    from datetime import datetime
    import traceback
    
    formatted = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': record.levelname,
        'logger_name': record.name,
        'message': record.getMessage(),
        'module': record.module,
        'function': record.funcName,
        'line_number': record.lineno
    }

    # Add exception info if present
    if record.exc_info:
        formatted['exception'] = {
            'type': record.exc_info[0].__name__,
            'message': str(record.exc_info[1]),
            'traceback': traceback.format_exception(*record.exc_info)
        }

    # Add extra attributes
    if hasattr(record, 'extra'):
        formatted['extra'] = record.extra

    return formatted
