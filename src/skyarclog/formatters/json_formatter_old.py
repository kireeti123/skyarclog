"""JSON formatter for message formatting."""

import json
from typing import Any, Dict
from .base_formatter import BaseFormatter


class JsonTransformer(BaseFormatter):
    """JSON message formatter."""

    def __init__(self):
        """Initialize the JSON formatter."""
        self.indent = None
        self.sort_keys = False

    def configure(self, indent: int = None, sort_keys: bool = False) -> None:
        """Configure the formatter.
        
        Args:
            indent: Number of spaces for indentation (default: None)
            sort_keys: Whether to sort dictionary keys (default: False)
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def transform(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a log message to JSON format.
        
        Args:
            message: Original log message
            
        Returns:
            Dict[str, Any]: Message with JSON formatting
        """
        # Convert any non-serializable objects to strings
        transformed = {}
        for key, value in message.items():
            try:
                json.dumps(value)
                transformed[key] = value
            except (TypeError, ValueError):
                transformed[key] = str(value)

        return transformed
