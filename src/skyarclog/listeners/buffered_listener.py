"""Base class for listeners that implement buffering functionality."""

import threading
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from .base_listener import BaseListener


class BufferedListener(BaseListener):
    """Base class for listeners that need to buffer records before processing.
    
    This class provides buffering functionality with:
    - Maximum buffer size control
    - Periodic flushing
    - Thread-safe operations
    - Batch processing
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the buffered listener.
        
        Args:
            config: Configuration dictionary containing:
                buffer: Dict with:
                    enabled: bool - Whether buffering is enabled
                    max_size: int - Maximum number of records to buffer
                    flush_interval: int - Seconds between automatic flushes
                    batch_size: int - Number of records to process in one batch
        """
        super().__init__(config)
        
        # Get buffer config with defaults
        buffer_config = config.get('buffer', {})
        self._buffering_enabled = buffer_config.get('enabled', True)
        self._max_buffer_size = buffer_config.get('max_size', 1000)
        self._flush_interval = buffer_config.get('flush_interval', 30)
        self._batch_size = buffer_config.get('batch_size', 100)
        
        # Initialize buffer and lock
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_lock = threading.Lock()
        
        # Initialize last flush time
        self._last_flush = datetime.now()
        
        # Start flush timer if buffering is enabled
        if self._buffering_enabled:
            self._start_flush_timer()
    
    def _start_flush_timer(self) -> None:
        """Start the background flush timer thread."""
        self._flush_timer = threading.Thread(
            target=self._flush_timer_loop,
            daemon=True
        )
        self._flush_timer.start()
    
    def _flush_timer_loop(self) -> None:
        """Background thread that periodically flushes the buffer."""
        while True:
            time.sleep(1)  # Check every second
            
            # Skip if not enough time has passed
            if datetime.now() - self._last_flush < timedelta(seconds=self._flush_interval):
                continue
                
            # Attempt to flush
            try:
                self.flush()
            except Exception as e:
                # Log error but don't crash the timer thread
                print(f"Error in flush timer: {str(e)}")
            
            self._last_flush = datetime.now()
    
    def emit(self, record: Dict[str, Any]) -> None:
        """Buffer the record and flush if needed.
        
        Args:
            record: Log record to emit
        """
        if not self._buffering_enabled:
            # If buffering is disabled, process immediately
            self._process_records([record])
            return
            
        with self._buffer_lock:
            # Add to buffer
            self._buffer.append(record)
            
            # Check if we need to flush
            if len(self._buffer) >= self._max_buffer_size:
                self.flush()
    
    def flush(self) -> None:
        """Process all buffered records in batches."""
        if not self._buffer:
            return
            
        with self._buffer_lock:
            # Process in batches
            buffer = self._buffer
            self._buffer = []  # Clear the buffer
        
        # Process the records in batches
        for i in range(0, len(buffer), self._batch_size):
            batch = buffer[i:i + self._batch_size]
            try:
                self._process_records(batch)
            except Exception as e:
                # If processing fails, try to handle with retry logic
                if not self._handle_failed_batch(batch, e):
                    # If retry fails, add back to buffer if there's space
                    with self._buffer_lock:
                        if len(self._buffer) + len(batch) <= self._max_buffer_size:
                            self._buffer.extend(batch)
    
    def _handle_failed_batch(self, batch: List[Dict[str, Any]], error: Exception) -> bool:
        """Handle a failed batch with retry logic.
        
        Args:
            batch: The batch of records that failed
            error: The exception that occurred
            
        Returns:
            bool: True if the batch was eventually processed, False if it failed
        """
        retry_config = self.config.get('retry', {})
        if not retry_config.get('enabled', False):
            return False
            
        max_retries = retry_config.get('max_retries', 3)
        initial_delay = retry_config.get('initial_delay', 1)
        max_delay = retry_config.get('max_delay', 60)
        exponential_base = retry_config.get('exponential_base', 2)
        
        # Try to process with exponential backoff
        for retry in range(max_retries):
            # Calculate delay with exponential backoff
            delay = min(
                initial_delay * (exponential_base ** retry),
                max_delay
            )
            
            # Wait before retry
            time.sleep(delay)
            
            try:
                self._process_records(batch)
                return True
            except Exception:
                continue
                
        return False
    
    def _process_records(self, records: List[Dict[str, Any]]) -> None:
        """Process a batch of records.
        
        This method must be implemented by subclasses to define how to process
        the records (e.g., send to a service, write to storage, etc.)
        
        Args:
            records: List of records to process
        """
        raise NotImplementedError(
            "Buffered listeners must implement _process_records"
        )
    
    def close(self) -> None:
        """Close the listener and flush any remaining records."""
        self.flush()
        super().close()
