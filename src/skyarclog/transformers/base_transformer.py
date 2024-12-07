"""Base transformer interface for message transformation."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTransformer(ABC):
    """Abstract base class for message transformers."""

    @abstractmethod
    def transform(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a log message.
        
        Args:
            message: Original log message
            
        Returns:
            Dict[str, Any]: Transformed message
        """
        pass
