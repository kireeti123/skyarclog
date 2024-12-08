"""SQL transformer for converting log messages to SQL-friendly format."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from .base_transformer import BaseTransformer

class SqlTransformer(BaseTransformer):
    """Transformer that converts log messages to SQL-friendly format."""

    def __init__(self):
        """Initialize SQL transformer."""
        self._date_format = '%Y-%m-%d %H:%M:%S.%f'
        self._max_field_length = 4000
        self._custom_mappings = {}

    def configure(self, date_format: str = '%Y-%m-%d %H:%M:%S.%f', 
                  max_field_length: int = 4000, 
                  custom_mappings: Optional[Dict[str, str]] = None) -> None:
        """Configure the transformer.
        
        Args:
            date_format: Format for datetime fields (default: '%Y-%m-%d %H:%M:%S.%f')
            max_field_length: Maximum length for text fields (default: 4000)
            custom_mappings: Field name mappings (default: None)
        """
        self._date_format = date_format
        self._max_field_length = max_field_length
        self._custom_mappings = custom_mappings or {}

    def transform(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Transform log message to SQL-friendly format.
        
        Args:
            message: Original log message
            
        Returns:
            SQL-friendly dictionary with:
            - All dates as formatted strings
            - JSON for nested structures
            - Truncated text fields
            - Mapped field names
        """
        sql_message = {}
        
        for key, value in message.items():
            # Apply custom field mapping if exists
            mapped_key = self._custom_mappings.get(key, key)
            
            # Transform value based on type
            transformed_value = self._transform_value(value)
            
            sql_message[mapped_key] = transformed_value
            
        return sql_message

    def _transform_value(self, value: Any) -> Union[str, int, float, None]:
        """Transform a value to SQL-friendly format.
        
        Args:
            value: Value to transform
            
        Returns:
            SQL-friendly value
        """
        if value is None:
            return None
            
        if isinstance(value, (int, float)):
            return value
            
        if isinstance(value, datetime):
            return value.strftime(self._date_format)
            
        if isinstance(value, (dict, list)):
            # Convert complex types to JSON string
            json_str = json.dumps(value)
            if len(json_str) > self._max_field_length:
                json_str = json_str[:self._max_field_length - 3] + '...'
            return json_str
            
        # Convert to string and truncate if needed
        str_value = str(value)
        if len(str_value) > self._max_field_length:
            return str_value[:self._max_field_length - 3] + '...'
            
        return str_value

    def get_column_definitions(self) -> List[Dict[str, str]]:
        """Get SQL column definitions for common log fields.
        
        Returns:
            List of column definitions with name and type
        """
        return [
            {'name': 'Id', 'type': 'BIGINT IDENTITY(1,1) PRIMARY KEY'},
            {'name': 'Timestamp', 'type': 'DATETIME2'},
            {'name': 'Level', 'type': 'NVARCHAR(10)'},
            {'name': 'Message', 'type': 'NVARCHAR(MAX)'},
            {'name': 'Logger', 'type': 'NVARCHAR(100)'},
            {'name': 'ThreadId', 'type': 'NVARCHAR(100)'},
            {'name': 'ProcessId', 'type': 'NVARCHAR(100)'},
            {'name': 'Exception', 'type': 'NVARCHAR(MAX)'},
            {'name': 'Properties', 'type': 'NVARCHAR(MAX)'},
            {'name': 'CorrelationId', 'type': 'NVARCHAR(100)'},
            {'name': 'ApplicationName', 'type': 'NVARCHAR(100)'},
            {'name': 'Environment', 'type': 'NVARCHAR(50)'}
        ]
