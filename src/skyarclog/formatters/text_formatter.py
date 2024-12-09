"""Text formatter implementation."""

from typing import Dict, Any
from .base_formatter import BaseFormatter

class TextFormatter(BaseFormatter):
    """Formats log messages as plain text."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize text formatter.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        self._config = config
        self._max_length = self._config.get('max_length', 0)
        self._include_timestamp = self._config.get('include_timestamp', True)

    def format(self, message: Dict[str, Any]) -> str:
        """Format the message as text.
        
        Args:
            message: Message to format
            
        Returns:
            Formatted text message
        """
        text = str(message.get('message', ''))
        
        if self._max_length > 0:
            text = text[:self._max_length]
            
        if self._include_timestamp and 'timestamp' in message:
            text = f"{message['timestamp']} - {text}"
            
        return text
