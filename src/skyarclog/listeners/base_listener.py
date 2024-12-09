"""Base listener interface for SkyArcLog."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..formatters.base_formatter import BaseFormatter
import logging

class BaseListener(ABC):
    """Abstract base class for all log listeners."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the listener.
        
        Args:
            config: Listener configuration
        """
        self._config = config
        self._formatters: List[BaseFormatter] = []
        self._enabled: bool = True
        self._name: Optional[str] = None
        self._setup_formatters()

    def _setup_formatters(self) -> None:
        """Set up the formatters based on configuration."""
        from ..formatters import create_formatter

        formatter_name = self._config.get('formatter')
        if formatter_name:
            try:
                formatter_config = self.get_formatter_config(formatter_name)
                self._formatters.append(create_formatter(formatter_name, formatter_config))
            except Exception as e:
                logging.warning(f"Failed to create formatter {formatter_name}: {e}")

    def get_formatter_config(self, format_name: str) -> Dict[str, Any]:
        """Get formatter configuration from global formatters section.
        
        Args:
            format_name: Name of the format/formatter
            
        Returns:
            Formatter configuration dictionary
        """
        formatters_config = self._config.get('formatters', {})
        return formatters_config.get(format_name, {})

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

    def add_formatter(self, formatter: BaseFormatter) -> None:
        """Add a message formatter.
        
        Args:
            formatter: Transformer to add
        """
        self._formatters.append(formatter)

    def _apply_formatters(self, message: Any) -> Dict[str, Any]:
        """Apply all registered formatters to the message.
        
        Args:
            message: Original log message
        
        Returns:
            Transformed message
        """
        # Ensure message is a dictionary
        if not isinstance(message, dict):
            message = {'message': str(message)}
        
        transformed_message = message.copy()
        
        # Apply all formatters
        for formatter in self._formatters:
            # Ensure formatter returns a dictionary
            result = formatter.transform(transformed_message)
            if isinstance(result, dict):
                transformed_message = result
            else:
                transformed_message['message'] = str(result)
        
        # Ensure application name is added if not present
        if 'application' not in transformed_message:
            transformed_message['application'] = self._config.get('application', 'Application')
        
        return transformed_message

    def format_message(self, message: Dict[str, Any]) -> Any:
        """Format the message using the configured formatter.
        
        Args:
            message: Message to format
            
        Returns:
            Formatted message
        """
        if self._formatters:
            return self._apply_formatters(message)
        return message

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
