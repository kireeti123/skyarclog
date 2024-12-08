"""Base listener interface for SkyArcLog."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..transformers.base_transformer import BaseTransformer


class BaseListener(ABC):
    """Abstract base class for all log listeners."""

    def __init__(self):
        """Initialize the listener."""
        self._transformers: List[BaseTransformer] = []
        self._enabled: bool = True
        self._name: Optional[str] = None
        self._config: Dict[str, Any] = {}

    @abstractmethod
    def initialize(self, name: str, config: Dict[str, Any]) -> None:
        """Initialize the listener with configuration.
        
        Args:
            name: Name of the listener instance
            config: Configuration dictionary for the listener
        """
        self._name = name
        self._enabled = config.get('enabled', True)
        self._config = config

    @abstractmethod
    def handle(self, message: Dict[str, Any]) -> None:
        """Handle a log message.
        
        Args:
            message: Log message to handle
        """
        pass

    def add_transformer(self, transformer: BaseTransformer) -> None:
        """Add a message transformer.
        
        Args:
            transformer: Transformer to add
        """
        self._transformers.append(transformer)

    def _apply_transformers(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all registered transformers to the message.
        
        Args:
            message: Original log message
        
        Returns:
            Transformed message
        """
        transformed_message = message.copy()
        
        # Apply all transformers
        for transformer in self._transformers:
            transformed_message = transformer.transform(transformed_message)
        
        # Ensure application name is added if not present
        if 'application' not in transformed_message:
            transformed_message['application'] = self._config.get('application', 'Application')
        
        return transformed_message

    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered messages."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Clean up resources."""
        pass

    @property
    def enabled(self) -> bool:
        """Get whether the listener is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self._enabled

    @property
    def name(self) -> Optional[str]:
        """Get the listener name.
        
        Returns:
            Optional[str]: Listener name if set, None otherwise
        """
        return self._name
