"""Memory listener implementation."""

from typing import Dict, Any, List
from collections import deque
from ..base_listener import BaseListener

class MemoryListener(BaseListener):
    """Listener that stores log messages in memory."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize memory listener.
        
        Args:
            config: Listener configuration
        """
        super().__init__(config)
        self._max_size = self._config.get('max_size', 1000)
        self._messages = deque(maxlen=self._max_size)

    def emit(self, message: Dict[str, Any]) -> None:
        """Store message in memory.
        
        Args:
            message: Message to store
        """
        formatted_message = self.format_message(message)
        self._messages.append(formatted_message)

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all stored messages.
        
        Returns:
            List of stored messages
        """
        return list(self._messages)

    def clear(self) -> None:
        """Clear all stored messages."""
        self._messages.clear()

    def close(self) -> None:
        """Clean up resources."""
        self.clear()
