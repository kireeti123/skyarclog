"""
Base formatter class for advanced logging framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseFormatter(ABC):
    """
    Abstract base class for log formatters
    """
    @abstractmethod
    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format a log entry
        
        :param log_entry: Dictionary containing log information
        :return: Formatted log string
        """
        pass
