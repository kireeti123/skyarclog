"""Protobuf message formatter for log messages."""

from typing import Any, Dict, Optional
import json
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct
from .base_formatter import BaseFormatter

class ProtobufFormatter(BaseFormatter):
    """Converts log messages to Protobuf Struct format."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Protobuf formatter.
        
        Args:
            config: Configuration dictionary for formatter
                - include_fields: Optional list of fields to include
                - exclude_fields: Optional list of fields to exclude
        """
        self.config = config or {}
        self.include_fields = self.config.get('include_fields', None)
        self.exclude_fields = self.config.get('exclude_fields', [])

    def _filter_dict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Filter dictionary based on include and exclude rules.
        
        Args:
            input_dict: Dictionary to filter
            
        Returns:
            Filtered dictionary
        """
        if self.include_fields:
            return {k: v for k, v in input_dict.items() if k in self.include_fields}
        
        return {k: v for k, v in input_dict.items() if k not in self.exclude_fields}

    def transform(self, message: Any, **kwargs) -> Struct:
        """Transform log message to Protobuf Struct.
        
        Args:
            message: Log message to transform
            **kwargs: Additional context for transformation
        
        Returns:
            Protobuf Struct representation of the log message
        """
        # If message is a string, create a dictionary
        if isinstance(message, str):
            message = {'message': message}
        
        # Add any additional context from kwargs
        if kwargs:
            message.update(kwargs)
        
        # Ensure message is a dictionary
        if not isinstance(message, dict):
            message = {'original_message': str(message)}
        
        # Filter dictionary if needed
        filtered_message = self._filter_dict(message)
        
        # Convert to Protobuf Struct
        protobuf_struct = Struct()
        json_format.ParseDict(filtered_message, protobuf_struct)
        
        return protobuf_struct
