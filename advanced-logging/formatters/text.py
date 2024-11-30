"""
Text formatter for advanced logging framework.
"""

import datetime
from typing import Dict, Any
from .base import BaseFormatter

class TextFormatter(BaseFormatter):
    """
    Simple text-based log formatter
    """
    def __init__(self, template: str = "[{level}] {timestamp} - {message}"):
        """
        Initialize with a custom formatting template
        
        :param template: String template for log formatting
        """
        self.template = template

    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format log entry to text
        
        :param log_entry: Dictionary containing log information
        :return: Formatted text log
        """
        # Merge extra context into the log entry
        formatted_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            **log_entry,
            **log_entry.get('extra', {})
        }
        
        return self.template.format(**formatted_entry)
