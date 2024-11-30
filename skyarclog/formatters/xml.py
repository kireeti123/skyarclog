"""
XML formatter for advanced logging framework.
"""

import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Any
from .base import BaseFormatter

class XMLFormatter(BaseFormatter):
    """
    XML-based log formatter
    """
    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format log entry to XML
        
        :param log_entry: Dictionary containing log information
        :return: XML formatted log
        """
        # Create root element
        root = ET.Element('log_entry')
        
        # Add timestamp
        timestamp = datetime.datetime.now().isoformat()
        ET.SubElement(root, 'timestamp').text = timestamp
        
        # Add core log entry fields
        for key, value in log_entry.items():
            if key == 'extra':
                # Handle extra context
                extra_elem = ET.SubElement(root, 'extra')
                for extra_key, extra_value in value.items():
                    ET.SubElement(extra_elem, extra_key).text = str(extra_value)
            else:
                ET.SubElement(root, key).text = str(value)
        
        # Convert to string
        return ET.tostring(root, encoding='unicode')
