"""Memory logging handler with interval-based flushing for skyarclog."""

import logging
import time
from logging.handlers import MemoryHandler
from typing import Optional, Callable, List

from pythonjsonlogger import jsonlogger


class MemoryHandlerWithInterval(MemoryHandler):
    """Memory handler that flushes based on both capacity and time interval."""

    def __init__(self, capacity: int, target: logging.Handler, interval: float = 0.0):
        """Initialize the memory handler.
        
        Args:
            capacity (int): Maximum number of records to buffer
            target (logging.Handler): Target handler to flush records to
            interval (float): Time interval in seconds between flushes (default: 0.0)
        """
        super().__init__(capacity, target=target)
        self.interval = interval
        self.last_flush = time.time()

    def shouldFlush(self, record: logging.LogRecord) -> bool:
        """Check if the buffer should be flushed.
        
        Args:
            record (logging.LogRecord): Current log record
            
        Returns:
            bool: True if buffer should be flushed, False otherwise
        """
        if super().shouldFlush(record):
            return True
            
        if self.interval > 0:
            current_time = time.time()
            if current_time - self.last_flush >= self.interval:
                self.last_flush = current_time
                return True
                
        return False


def create_memory_handler(
    capacity: int = 1000,
    flush_interval: float = 10.0,
    target_handler_config: dict = None,
    target_handler_creator: Optional[Callable] = None,
    formatter: Optional[logging.Formatter] = None,
    level: str = 'INFO'
) -> logging.Handler:
    """Create a memory handler with interval-based flushing.
    
    Args:
        capacity (int): Maximum number of records to buffer (default: 1000)
        flush_interval (float): Time interval in seconds between flushes (default: 10.0)
        target_handler_config (dict): Configuration for the target handler
        target_handler_creator (Optional[Callable]): Function to create the target handler
        formatter (Optional[logging.Formatter]): Custom formatter (default: JsonFormatter)
        level (str): Logging level (default: 'INFO')
        
    Returns:
        logging.Handler: Configured memory handler
        
    Raises:
        ValueError: If target_handler_config or target_handler_creator is not provided
    """
    if not target_handler_config or not target_handler_creator:
        raise ValueError("Both target_handler_config and target_handler_creator must be provided")

    target_handler = target_handler_creator(target_handler_config)
    
    handler = MemoryHandlerWithInterval(
        capacity=capacity,
        target=target_handler,
        interval=flush_interval
    )
    
    handler.setLevel(getattr(logging, level.upper()))
    
    if formatter is None:
        formatter = jsonlogger.JsonFormatter()
    
    handler.setFormatter(formatter)
    return handler
