"""
Base listener class for advanced logging framework.
"""

from abc import ABC, abstractmethod

class BaseListener(ABC):
    """
    Abstract base class for log listeners
    """
    @abstractmethod
    def emit(self, log_entry: str):
        """
        Emit a log entry
        
        :param log_entry: Formatted log entry to emit
        """
        pass
