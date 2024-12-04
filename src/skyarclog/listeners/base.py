"""
Base listener implementation for skyarclog.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

class BaseListener(ABC):
    """Base class for all listeners."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the listener with configuration."""
        self.config = config
        self.enabled = config.get('enabled', True)
        self.supports_batching = False  # Override in subclasses that support batching
        
    @abstractmethod
    def handle(self, log_record: Dict[str, Any]) -> bool:
        """
        Handle a single log record.
        
        Args:
            log_record: Dictionary containing log record information
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def handle_batch(self, batch: List[Dict[str, Any]]) -> bool:
        """
        Handle a batch of log records.
        
        Args:
            batch: List of log record dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.supports_batching:
            # Process records individually if batching not supported
            success = True
            for record in batch:
                if not self.handle(record):
                    success = False
            return success
            
        # Should be implemented by listeners that support batching
        raise NotImplementedError("Batch processing not implemented for this listener")
        
    def flush(self) -> None:
        """Flush any buffered records."""
        pass
        
    def close(self) -> None:
        """Clean up resources."""
        pass
        
class BufferedListener(BaseListener):
    """Base class for listeners that support buffered operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the buffered listener."""
        super().__init__(config)
        self.supports_batching = True
        self.max_batch_size = config.get('batch_size', 100)
        self.flush_interval = config.get('flush_interval', 1.0)
        
    @abstractmethod
    def handle_batch(self, batch: List[Dict[str, Any]]) -> bool:
        """
        Handle a batch of log records.
        Must be implemented by buffered listeners.
        
        Args:
            batch: List of log record dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
