"""Base class for buffered listeners."""

import queue
import threading
import time
from typing import Any, Dict, List, Optional
from threading import Lock, Thread, Event
from .base_listener import BaseListener


class BufferedListener(BaseListener):
    """Base class for listeners that buffer messages."""

    def __init__(self):
        """Initialize the buffered listener."""
        super().__init__()
        self._buffer: Optional[queue.Queue] = None
        self._batch_lock = Lock()
        self._shutdown_event = Event()
        self._worker_thread: Optional[Thread] = None
        
        # Buffering configuration
        self._buffering_enabled: bool = False
        self._max_buffer_size: int = 1000
        self._flush_interval: float = 60.0  # seconds
        self._batch_size: int = 100
        
        # Retry configuration
        self._retry_enabled: bool = False
        self._retry_config = {
            'max_retries': 3,
            'initial_delay': 1,
            'max_delay': 60,
            'exponential_base': 2
        }

    def initialize(self, name: str, config: Dict[str, Any]) -> None:
        """Initialize the buffered listener.
        
        Args:
            name: Name of the listener instance
            config: Configuration dictionary containing:
                - buffer.enabled: Whether buffering is enabled
                - buffer.max_size: Maximum number of messages to buffer
                - buffer.flush_interval: Interval in seconds between flushes
                - buffer.batch_size: Number of messages to send in one batch
                - retry.enabled: Whether retry is enabled
                - retry: Retry configuration for failed batches
        """
        super().initialize(name, config)
        
        # Initialize buffering if enabled
        buffer_config = config.get('buffer', {})
        self._buffering_enabled = buffer_config.get('enabled', False)
        
        if self._buffering_enabled:
            self._buffer = queue.Queue(maxsize=buffer_config.get('max_size', 1000))
            self._max_buffer_size = buffer_config.get('max_size', 1000)
            self._flush_interval = buffer_config.get('flush_interval', 60.0)
            self._batch_size = buffer_config.get('batch_size', 100)
            # Start worker thread only if buffering is enabled
            self._start_worker()
        
        # Initialize retry if enabled
        retry_config = config.get('retry', {})
        self._retry_enabled = retry_config.get('enabled', False)
        if self._retry_enabled:
            self._retry_config.update(retry_config)

    def handle_log(self, message: Dict[str, Any]) -> None:
        """Handle a log message by buffering it or sending directly.
        
        Args:
            message: Message to handle
        """
        if not self._enabled:
            return

        if self._buffering_enabled:
            try:
                self._buffer.put(message, block=True, timeout=1)
            except queue.Full:
                print(f"Buffer full in {self.name}, dropping message")
        else:
            # If buffering is disabled, send immediately
            self._send_with_retry([message])

    def flush(self) -> None:
        """Flush buffered messages in batches."""
        if not self._buffering_enabled or not self._buffer:
            return

        with self._batch_lock:
            batch = []
            while len(batch) < self._batch_size:
                try:
                    message = self._buffer.get_nowait()
                    batch.append(message)
                except queue.Empty:
                    break
            
            if batch:
                self._send_with_retry(batch)

    def close(self) -> None:
        """Clean up resources."""
        self._shutdown_event.set()
        
        if self._buffering_enabled:
            if self._worker_thread and self._worker_thread.is_alive():
                self._worker_thread.join(timeout=self._flush_interval + 5)
            # Flush remaining messages
            self.flush()

    def _start_worker(self) -> None:
        """Start the worker thread if buffering is enabled."""
        if self._buffering_enabled:
            self._worker_thread = Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()

    def _worker_loop(self) -> None:
        """Main worker loop for processing buffered messages."""
        while not self._shutdown_event.is_set():
            try:
                self.flush()
            except Exception as e:
                print(f"Error in worker loop of {self.name}: {e}")
            
            # Wait for next interval or shutdown
            self._shutdown_event.wait(timeout=self._flush_interval)

    def _send_with_retry(self, batch: List[Dict[str, Any]]) -> None:
        """Send a batch of messages with optional retry logic.
        
        Args:
            batch: List of messages to send
        """
        if not self._retry_enabled:
            # If retry is disabled, just try once
            try:
                self._send_batch(batch)
            except Exception as e:
                print(f"Send failed in {self.name} (retry disabled): {e}")
            return

        retry_count = 0
        delay = self._retry_config['initial_delay']
        
        while retry_count < self._retry_config['max_retries']:
            try:
                self._send_batch(batch)
                return
            except Exception as e:
                retry_count += 1
                if retry_count >= self._retry_config['max_retries']:
                    print(f"Final retry failed in {self.name}: {e}")
                    # Could implement dead letter queue here
                    return
                
                print(f"Retry {retry_count} failed in {self.name}: {e}")
                time.sleep(min(delay, self._retry_config['max_delay']))
                delay *= self._retry_config['exponential_base']

    def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Send a batch of messages.
        
        Args:
            batch: List of messages to send
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _send_batch")
