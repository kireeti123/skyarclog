"""JSON transformer for message formatting."""

import json
from typing import Any, Dict
from .base_transformer import BaseTransformer


class JsonTransformer(BaseTransformer):
    """Transformer that formats messages as JSON."""

    def __init__(self):
        """Initialize the JSON transformer."""
        self.indent = None
        self.sort_keys = False

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the transformer.
        
        Args:
            config: Configuration dictionary containing:
                - indent: Number of spaces for indentation (default: None)
                - sort_keys: Whether to sort dictionary keys (default: False)
        """
        self.indent = config.get('indent')
        self.sort_keys = config.get('sort_keys', False)

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
