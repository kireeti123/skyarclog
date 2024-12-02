"""
CSV formatter for advanced logging framework.
"""

import csv
import io
import datetime
from typing import Dict, Any
from .base import BaseFormatter

class CSVFormatter(BaseFormatter):
    """
    CSV-based log formatter
    """
    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format log entry to CSV
        
        :param log_entry: Dictionary containing log information
        :return: CSV formatted log
        """
        # Prepare output buffer
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Add timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Prepare row with core fields and extra context
        row = [
            timestamp,
            log_entry.get('level', ''),
            log_entry.get('message', '')
        ]
        
        # Add extra context fields
        extra = log_entry.get('extra', {})
        for key, value in extra.items():
            row.append(f"{key}:{value}")
        
        # Write row
        writer.writerow(row)
        
        return output.getvalue().strip()
