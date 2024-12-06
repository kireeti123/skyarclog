"""Console logging handler for skyarclog."""

import logging
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger


def create_console_handler(
    stream=sys.stdout,
    level: str = 'INFO',
    formatter: Optional[logging.Formatter] = None
) -> logging.Handler:
    """Create a console logging handler.
    
    Args:
        stream: Stream to write to (default: sys.stdout)
        level (str): Logging level (default: 'INFO')
        formatter (Optional[logging.Formatter]): Custom formatter (default: JsonFormatter)
        
    Returns:
        logging.Handler: Configured console handler
    """
    handler = logging.StreamHandler(stream)
    handler.setLevel(getattr(logging, level.upper()))
    
    if formatter is None:
        formatter = jsonlogger.JsonFormatter()
    
    handler.setFormatter(formatter)
    return handler
