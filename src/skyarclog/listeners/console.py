"""
Console listener for advanced logging framework.
"""

import sys
from .base import BaseListener

class ConsoleListener(BaseListener):
    """
    Listener that outputs logs to console
    """
    def __init__(self, stream=sys.stdout):
        """
        Initialize console listener
        
        :param stream: Output stream (default: sys.stdout)
        """
        self.stream = stream

    def emit(self, log_entry: str):
        """
        Print log entry to console
        
        :param log_entry: Formatted log entry
        """
        print(log_entry, file=self.stream)
