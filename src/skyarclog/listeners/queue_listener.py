"""Queue listener implementation."""

from typing import Dict, Any
import queue
import threading
from ..base_listener import BaseListener

class QueueListener(BaseListener):
    """Listener that writes log messages to a queue."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize queue listener.
        
        Args:
            config: Listener configuration
        """
        super().__init__(config)
        self._queue = queue.Queue(maxsize=self._config.get('max_size', 1000))
        self._worker_thread = None
        self._stop_event = threading.Event()
        self._start_worker()

    def _start_worker(self) -> None:
        """Start the worker thread."""
        self._worker_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self._worker_thread.start()

    def _process_queue(self) -> None:
        """Process messages from the queue."""
        while not self._stop_event.is_set():
            try:
                # Get message with timeout to allow checking stop event
                message = self._queue.get(timeout=0.1)
                self._handle_message(message)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing message: {e}")

    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle a single message from the queue.
        
        Args:
            message: Message to handle
        """
        # Format the message
        formatted_message = self.format_message(message)
        
        # Process the message (override in subclass)
        self._process_message(formatted_message)

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a formatted message.
        
        Args:
            message: Message to process
        """
        # Default implementation just prints the message
        # Override this in subclasses for specific processing
        print(message)

    def emit(self, message: Dict[str, Any]) -> None:
        """Add message to the queue.
        
        Args:
            message: Message to queue
        """
        try:
            self._queue.put(message, block=False)
        except queue.Full:
            print("Queue is full, message dropped")

    def close(self) -> None:
        """Stop the worker thread and clean up."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
            self._worker_thread = None
