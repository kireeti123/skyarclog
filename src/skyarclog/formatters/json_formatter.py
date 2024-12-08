"""JSON message formatter."""

import json
from datetime import datetime
from typing import Any, Dict
from .base_formatter import BaseFormatter


class JsonFormatter(BaseFormatter):
    """Formats log messages as JSON."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the formatter.
        
        Args:
            config: Formatter configuration containing:
                - timestamp_format: Format for timestamps
                - include_fields: List of fields to include
                - exclude_fields: List of fields to exclude
        """
        self.config = config or {}
        self.timestamp_format = self.config.get('timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
        self.indent = self.config.get('indent', 2)
        self.sort_keys = self.config.get('sort_keys', False)

    def transform(self, message: Any, **kwargs) -> str:
        """Transform the log message into a JSON-formatted string.
        
        Args:
            message: Log message to transform
            **kwargs: Additional context for transformation
        
        Returns:
            JSON-formatted log message
        """
        # If message is already a dictionary, just JSON serialize it
        if isinstance(message, dict):
            return json.dumps(message, indent=self.indent, sort_keys=self.sort_keys)
        
        # If message is a string, create a simple dictionary
        log_entry = {
            'message': str(message),
            'timestamp': datetime.now().strftime(self.timestamp_format)
        }
        
        # Add any additional context from kwargs
        log_entry.update(kwargs)
        
        return json.dumps(log_entry, indent=self.indent, sort_keys=self.sort_keys)
