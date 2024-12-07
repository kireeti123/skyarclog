"""JSON message formatter."""

import json
from datetime import datetime
from typing import Any, Dict
from .base_transformer import BaseTransformer


class JsonFormatter(BaseTransformer):
    """Formats log messages as JSON."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the formatter.
        
        Args:
            config: Formatter configuration containing:
                - timestamp_format: Format for timestamps
                - include_fields: List of fields to include
                - exclude_fields: List of fields to exclude
        """
        self.timestamp_format = config.get('timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
        self.include_fields = set(config.get('include_fields', []))
        self.exclude_fields = set(config.get('exclude_fields', []))

    def transform(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a log message to JSON format.
        
        Args:
            message: Original log message
            
        Returns:
            Dict[str, Any]: JSON-formatted message
        """
        # Start with a copy of the message
        formatted = message.copy()

        # Add timestamp if not present
        if 'timestamp' not in formatted:
            formatted['timestamp'] = datetime.utcnow().strftime(self.timestamp_format)

        # Filter fields
        if self.include_fields:
            formatted = {k: v for k, v in formatted.items() if k in self.include_fields}
        for field in self.exclude_fields:
            formatted.pop(field, None)

        return formatted
