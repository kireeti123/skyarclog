"""Base formatter for SkyArcLog logging framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseFormatter(ABC):
    """Abstract base class for log message formatters."""

    @abstractmethod
    def transform(self, message: Any, **kwargs) -> Any:
        """Transform a log message.
        
        Args:
            message: Log message to transform
            **kwargs: Additional context for transformation
        
        Returns:
            Transformed log message
        """
        pass
