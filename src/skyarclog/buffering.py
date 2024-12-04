"""
Buffered logging implementation using queues for improved performance.
This module provides a thread-safe queue-based buffering system for log messages.
"""

import queue
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class LogBuffer:
    """A thread-safe buffer for log messages using a queue system."""
    
    def __init__(self, 
                 max_batch_size: int = 100,
                 flush_interval: float = 1.0,
                 max_queue_size: int = 10000):
        """
        Initialize the log buffer.
        
        Args:
            max_batch_size: Maximum number of log messages to process in one batch
            flush_interval: Time in seconds between forced flush operations
            max_queue_size: Maximum number of messages that can be queued
        """
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.listeners: List[Any] = []
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.last_flush_time = time.time()
        self.buffer_lock = threading.Lock()
        
    def start(self):
        """Start the buffer processing thread."""
        self.worker_thread.start()
        
    def stop(self):
        """Stop the buffer processing thread and flush remaining messages."""
        self.stop_event.set()
        self.flush()  # Ensure all remaining messages are processed
        if self.worker_thread.is_alive():
            self.worker_thread.join()
            
    def add_listener(self, listener: Any):
        """Add a listener that will receive the batched log messages."""
        self.listeners.append(listener)
        
    def remove_listener(self, listener: Any):
        """Remove a listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)
            
    def enqueue(self, log_record: Dict[str, Any]):
        """
        Add a log record to the queue.
        
        Args:
            log_record: Dictionary containing log record information
        
        Returns:
            bool: True if enqueued successfully, False if queue is full
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in log_record:
                log_record['timestamp'] = datetime.utcnow().isoformat()
                
            self.queue.put_nowait(log_record)
            return True
        except queue.Full:
            logging.warning("Log buffer queue is full, message dropped")
            return False
            
    def flush(self):
        """Force a flush of the current buffer."""
        with self.buffer_lock:
            batch = []
            try:
                while not self.queue.empty() and len(batch) < self.max_batch_size:
                    batch.append(self.queue.get_nowait())
                    self.queue.task_done()
            except queue.Empty:
                pass
            
            if batch:
                self._process_batch(batch)
                
    def _process_queue(self):
        """Main worker thread that processes the queue."""
        while not self.stop_event.is_set():
            current_time = time.time()
            
            # Force flush if interval has elapsed
            if current_time - self.last_flush_time >= self.flush_interval:
                self.flush()
                self.last_flush_time = current_time
                
            # Process up to max_batch_size messages
            batch = []
            try:
                while len(batch) < self.max_batch_size:
                    # Wait for a short time for new messages
                    message = self.queue.get(timeout=0.1)
                    batch.append(message)
                    self.queue.task_done()
            except queue.Empty:
                pass
            
            if batch:
                self._process_batch(batch)
                
            time.sleep(0.01)  # Small sleep to prevent CPU spinning
            
    def _process_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of log messages."""
        if not batch:
            return
            
        # Send batch to all listeners
        for listener in self.listeners:
            try:
                listener.handle_batch(batch)
            except Exception as e:
                logging.error(f"Error in listener {listener.__class__.__name__}: {str(e)}")
                
class BufferedHandler(logging.Handler):
    """A logging handler that uses the LogBuffer for improved performance."""
    
    def __init__(self, 
                 buffer: Optional[LogBuffer] = None,
                 max_batch_size: int = 100,
                 flush_interval: float = 1.0,
                 max_queue_size: int = 10000):
        """
        Initialize the buffered handler.
        
        Args:
            buffer: Optional existing LogBuffer instance
            max_batch_size: Maximum number of log messages to process in one batch
            flush_interval: Time in seconds between forced flush operations
            max_queue_size: Maximum number of messages that can be queued
        """
        super().__init__()
        self.buffer = buffer or LogBuffer(
            max_batch_size=max_batch_size,
            flush_interval=flush_interval,
            max_queue_size=max_queue_size
        )
        self.buffer.start()
        
    def emit(self, record: logging.LogRecord):
        """Process a log record."""
        try:
            log_dict = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': self.format(record),
                'logger': record.name,
                'path': record.pathname,
                'line': record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'extra'):
                log_dict.update(record.extra)
                
            self.buffer.enqueue(log_dict)
        except Exception as e:
            self.handleError(record)
            
    def close(self):
        """Stop the buffer and clean up."""
        self.buffer.stop()
        super().close()
        
    def flush(self):
        """Force a flush of the buffer."""
        self.buffer.flush()
