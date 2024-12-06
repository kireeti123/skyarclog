"""Queue logging handler with batch processing for skyarclog."""

import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from typing import Optional, Callable, List, Any

from pythonjsonlogger import jsonlogger


class BatchQueueHandler(QueueHandler):
    """Queue handler that supports batch processing of log records."""

    def __init__(self, queue: queue.Queue, batch_size: int = 100):
        """Initialize the batch queue handler.
        
        Args:
            queue (queue.Queue): Queue to store records
            batch_size (int): Number of records to process in a batch (default: 100)
        """
        super().__init__(queue)
        self.batch_size = batch_size
        self.batch = []

    def enqueue(self, record: logging.LogRecord) -> None:
        """Add a record to the batch and enqueue if batch is full.
        
        Args:
            record (logging.LogRecord): Log record to process
        """
        self.batch.append(record)
        if len(self.batch) >= self.batch_size:
            self.flush_batch()

    def flush_batch(self) -> None:
        """Flush the current batch of records to the queue."""
        if self.batch:
            self.queue.put(self.batch)
            self.batch = []

    def close(self) -> None:
        """Close the handler and flush any remaining records."""
        self.flush_batch()
        super().close()


class BatchQueueListener(QueueListener):
    """Queue listener that processes batches of log records."""

    def dequeue(self) -> Optional[List[logging.LogRecord]]:
        """Dequeue a batch of records from the queue.
        
        Returns:
            Optional[List[logging.LogRecord]]: Batch of records or None if queue is empty
        """
        try:
            return self.queue.get(block=True, timeout=self.queue.empty())
        except queue.Empty:
            return None

    def _process_batch(self, batch: List[logging.LogRecord]) -> None:
        """Process a batch of records.
        
        Args:
            batch (List[logging.LogRecord]): Batch of records to process
        """
        for record in batch:
            for handler in self.handlers:
                if record.levelno >= handler.level:
                    handler.handle(record)

    def _process_next(self) -> None:
        """Process the next batch of records from the queue."""
        batch = self.dequeue()
        if batch:
            self._process_batch(batch)


def create_queue_handler(
    batch_size: int = 100,
    target_handlers_config: List[dict] = None,
    target_handler_creator: Optional[Callable] = None,
    formatter: Optional[logging.Formatter] = None,
    level: str = 'INFO'
) -> tuple[logging.Handler, QueueListener]:
    """Create a batch queue handler and its listener.
    
    Args:
        batch_size (int): Number of records to process in a batch (default: 100)
        target_handlers_config (List[dict]): Configuration for target handlers
        target_handler_creator (Optional[Callable]): Function to create target handlers
        formatter (Optional[logging.Formatter]): Custom formatter (default: JsonFormatter)
        level (str): Logging level (default: 'INFO')
        
    Returns:
        tuple[logging.Handler, QueueListener]: Configured queue handler and its listener
        
    Raises:
        ValueError: If target_handlers_config or target_handler_creator is not provided
    """
    if not target_handlers_config or not target_handler_creator:
        raise ValueError("Both target_handlers_config and target_handler_creator must be provided")

    log_queue = queue.Queue()
    handler = BatchQueueHandler(log_queue, batch_size=batch_size)
    handler.setLevel(getattr(logging, level.upper()))
    
    if formatter is None:
        formatter = jsonlogger.JsonFormatter()
    
    handler.setFormatter(formatter)

    # Create target handlers
    target_handlers = [
        target_handler_creator(config)
        for config in target_handlers_config
    ]

    # Create and start queue listener
    listener = BatchQueueListener(log_queue, *target_handlers)
    listener.start()

    return handler, listener
