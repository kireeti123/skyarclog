"""SQL formatter for converting log messages to SQL-friendly format."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from .base_formatter import BaseFormatter

class SqlFormatter(BaseFormatter):
    """Formatter that converts log messages to SQL-friendly format."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize SQL formatter.
        
        Args:
            config: Configuration dictionary with optional settings
        """
        config = config or {}
        self._date_format = config.get('date_format', '%Y-%m-%d %H:%M:%S.%f')
        self._max_field_length = config.get('max_field_length', 4000)
        self._custom_mappings = config.get('custom_mappings', {})

    def _transform_value(self, value: Any) -> Any:
        """Transform a single value to SQL-friendly format.
        
        Args:
            value: Value to transform
            
        Returns:
            Transformed value
        """
        if isinstance(value, datetime):
            return value.strftime(self._date_format)
        
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        
        if isinstance(value, str):
            return value[:self._max_field_length]
        
        return value

    def transform(self, message: Any, **kwargs) -> Dict[str, Any]:
        """Transform log message to SQL-friendly format.
        
        Args:
            message: Log message to transform
            **kwargs: Additional context
            
        Returns:
            SQL-friendly dictionary
        """
        # If message is a string, create a dictionary
        if isinstance(message, str):
            message = {
                'message': message,
                'timestamp': datetime.now().strftime(self._date_format)
            }
        
        # Add any additional context from kwargs
        if kwargs:
            message.update(kwargs)
        
        # Ensure message is a dictionary
        if not isinstance(message, dict):
            message = {'original_message': str(message)}
        
        # Transform the message
        sql_message = {}
        for key, value in message.items():
            # Apply custom field mapping if exists
            mapped_key = self._custom_mappings.get(key, key)
            
            # Transform value based on type
            transformed_value = self._transform_value(value)
            
            # Store transformed value
            sql_message[mapped_key] = transformed_value
        
        return sql_message
