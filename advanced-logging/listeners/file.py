"""
File listener for advanced logging framework.
"""

from .base import BaseListener

class FileListener(BaseListener):
    """
    Listener that writes logs to a file
    """
    def __init__(self, filename: str, mode: str = 'a'):
        """
        Initialize file listener
        
        :param filename: Path to log file
        :param mode: File open mode (default: append)
        """
        self.filename = filename
        self.mode = mode

    def emit(self, log_entry: str):
        """
        Write log entry to file
        
        :param log_entry: Formatted log entry
        """
        with open(self.filename, self.mode) as f:
            f.write(log_entry + '\n')
