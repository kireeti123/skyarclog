"""File logging handler for skyarclog."""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Union, Dict

from pythonjsonlogger import jsonlogger


def create_file_handler(
    filename: str,
    mode: str = 'a',
    encoding: str = 'utf-8',
    level: str = 'INFO',
    formatter: Optional[logging.Formatter] = None,
    rotation_config: Optional[Dict] = None
) -> logging.Handler:
    """Create a file logging handler with optional rotation.
    
    Args:
        filename (str): Path to the log file
        mode (str): File open mode (default: 'a' for append)
        encoding (str): File encoding (default: 'utf-8')
        level (str): Logging level (default: 'INFO')
        formatter (Optional[logging.Formatter]): Custom formatter (default: JsonFormatter)
        rotation_config (Optional[Dict]): Rotation configuration. Example:
            {
                "type": "size",  # or "time"
                "max_bytes": 10485760,  # 10MB, for size-based rotation
                "backup_count": 5,
                # For time-based rotation:
                "when": "midnight",  # 'S', 'M', 'H', 'D', 'W0'-'W6', 'midnight'
                "interval": 1
            }
        
    Returns:
        logging.Handler: Configured file handler
    """
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    if rotation_config:
        rotation_type = rotation_config.get('type', 'size')
        backup_count = rotation_config.get('backup_count', 5)
        
        if rotation_type == 'size':
            max_bytes = rotation_config.get('max_bytes', 10 * 1024 * 1024)  # Default: 10MB
            handler = RotatingFileHandler(
                filename=filename,
                mode=mode,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=encoding
            )
        else:  # time-based rotation
            when = rotation_config.get('when', 'midnight')
            interval = rotation_config.get('interval', 1)
            handler = TimedRotatingFileHandler(
                filename=filename,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding=encoding
            )
    else:
        handler = logging.FileHandler(filename, mode=mode, encoding=encoding)

    handler.setLevel(getattr(logging, level.upper()))
    
    if formatter is None:
        formatter = jsonlogger.JsonFormatter()
    
    handler.setFormatter(formatter)
    return handler
