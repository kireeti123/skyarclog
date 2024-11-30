"""
JSON formatter for advanced logging framework.
"""

import json
import datetime
from typing import Dict, Any
from .base import BaseFormatter

class JSONFormatter(BaseFormatter):
    """
    JSON-based log formatter
    """
    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format log entry to JSON
        
        :param log_entry: Dictionary containing log information
        :return: JSON formatted log
        """
        # Add timestamp and merge extra context
        formatted_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            **log_entry,
            **log_entry.get('extra', {})
        }
        
        return json.dumps(formatted_entry)
