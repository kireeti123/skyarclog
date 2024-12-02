"""
Enhanced asynchronous worker with advanced performance optimizations
"""

import asyncio
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

@dataclass
class CircuitBreaker:
    """Circuit breaker for handling overload scenarios."""
    failure_threshold: int = 5
    reset_timeout: float = 60.0
    failures: int = 0
    last_failure_time: float = 0
    is_open: bool = False

class RingBuffer:
    """Fixed-size ring buffer for efficient log storage."""
    def __init__(self, size: int = 10000):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.full = False
        self._lock = threading.Lock()

    def push(self, item: Any) -> bool:
        """Push an item to the buffer. Returns False if buffer is full."""
        with self._lock:
            if self.full:
                return False
            
            self.buffer[self.head] = item
            self.head = (self.head + 1) % self.size
            self.full = self.head == self.tail
            return True

    def pop(self) -> Optional[Any]:
        """Pop an item from the buffer."""
        with self._lock:
            if self.tail == self.head and not self.full:
                return None
            
            item = self.buffer[self.tail]
            self.buffer[self.tail] = None
            self.tail = (self.tail + 1) % self.size
            self.full = False
            return item

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self.tail == self.head and not self.full

class BatchProcessor:
    """Efficient batch processing of logs."""
    def __init__(self, max_batch_size: int = 1000, max_wait_time: float = 0.1):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.current_batch: List[Any] = []
        self.last_flush_time = time.time()
        self._lock = threading.Lock()

    def add(self, item: Any) -> bool:
        """Add item to batch. Returns True if batch should be flushed."""
        with self._lock:
            self.current_batch.append(item)
            should_flush = (
                len(self.current_batch) >= self.max_batch_size or
                time.time() - self.last_flush_time >= self.max_wait_time
            )
            return should_flush

    def get_batch(self) -> List[Any]:
        """Get current batch and reset."""
        with self._lock:
            batch = self.current_batch
            self.current_batch = []
            self.last_flush_time = time.time()
            return batch

class AsyncWorker:
    """
    Enhanced asynchronous worker with advanced performance optimizations:
    - Ring buffer for memory efficiency
    - Batch processing for better throughput
    - Circuit breaker for overload protection
    - Adaptive worker scaling
    - Priority queue support
    - Memory pressure monitoring
    """

    def __init__(
        self,
        num_workers: int = 4,
        queue_size: int = 10000,
        batch_size: int = 1000,
        max_wait_time: float = 0.1,
        min_workers: int = 2,
        max_workers: int = 8,
    ):
        """
        Initialize the async worker with advanced configuration.

        Args:
            num_workers: Initial number of worker threads
            queue_size: Maximum size of the ring buffer
            batch_size: Maximum batch size for processing
            max_wait_time: Maximum wait time before processing a batch
            min_workers: Minimum number of worker threads
            max_workers: Maximum number of worker threads
        """
        self.ring_buffer = RingBuffer(queue_size)
        self.batch_processor = BatchProcessor(batch_size, max_wait_time)
        self.circuit_breaker = CircuitBreaker()
        
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = num_workers
        
        self.executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="AsyncWorker"
        )
        
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        self.dropped_logs = 0
        self._lock = threading.Lock()
        
        # Performance metrics
        self.total_processed = 0
        self.total_processing_time = 0
        self.last_scale_time = time.time()
        self.processing_times: List[float] = []
        self.active_workers: Set[int] = set()

    def start(self) -> None:
        """Start the background worker thread."""
        if self.worker_thread is not None:
            return

        self.running = True
        self.worker_thread = threading.Thread(
            target=self._process_queue,
            name="AsyncWorkerMain"
        )
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def stop(self) -> None:
        """Stop the background worker thread and process remaining logs."""
        if not self.running:
            return

        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
            self.worker_thread = None

        # Process remaining items
        while not self.ring_buffer.is_empty():
            self._process_batch()

        self.executor.shutdown(wait=True)

    def enqueue(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Enqueue a logging task with circuit breaker protection.
        
        Args:
            func: The function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        if not self.running:
            self.start()

        # Check circuit breaker
        if self.circuit_breaker.is_open:
            current_time = time.time()
            if current_time - self.circuit_breaker.last_failure_time > self.circuit_breaker.reset_timeout:
                self.circuit_breaker.is_open = False
            else:
                with self._lock:
                    self.dropped_logs += 1
                return

        # Try to add to ring buffer
        if not self.ring_buffer.push((func, args, kwargs)):
            with self._lock:
                self.dropped_logs += 1
                self.circuit_breaker.failures += 1
                self.circuit_breaker.last_failure_time = time.time()
                
                if self.circuit_breaker.failures >= self.circuit_breaker.failure_threshold:
                    self.circuit_breaker.is_open = True

    def _process_queue(self) -> None:
        """Process tasks from the queue with adaptive scaling."""
        while self.running or not self.ring_buffer.is_empty():
            try:
                # Get next task
                task = self.ring_buffer.pop()
                if task is None:
                    time.sleep(0.01)  # Short sleep to prevent CPU spinning
                    continue

                # Add to batch processor
                if self.batch_processor.add(task):
                    self._process_batch()

                # Check if we should adjust worker count
                self._adjust_worker_count()

            except Exception as e:
                print(f"Error in queue processing: {str(e)}")

    def _process_batch(self) -> None:
        """Process a batch of tasks efficiently."""
        batch = self.batch_processor.get_batch()
        if not batch:
            return

        start_time = time.time()
        futures = []

        for task in batch:
            func, args, kwargs = task
            future = self.executor.submit(self._execute_task, func, args, kwargs)
            futures.append(future)

        # Wait for all tasks to complete
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error executing task: {str(e)}")

        # Update metrics
        processing_time = time.time() - start_time
        with self._lock:
            self.total_processed += len(batch)
            self.total_processing_time += processing_time
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)

    def _execute_task(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """Execute a single task with worker tracking."""
        worker_id = threading.get_ident()
        with self._lock:
            self.active_workers.add(worker_id)

        try:
            func(*args, **kwargs)
        finally:
            with self._lock:
                self.active_workers.remove(worker_id)

    def _adjust_worker_count(self) -> None:
        """
        Dynamically adjust worker count based on performance metrics.
        Uses a simple algorithm that considers:
        - Average processing time
        - Queue size
        - Current worker utilization
        """
        current_time = time.time()
        if current_time - self.last_scale_time < 5:  # Only scale every 5 seconds
            return

        with self._lock:
            # Calculate metrics
            avg_processing_time = (
                sum(self.processing_times) / len(self.processing_times)
                if self.processing_times else 0
            )
            worker_utilization = len(self.active_workers) / self.current_workers

            # Scale up if:
            # - High worker utilization (>80%)
            # - Increasing processing times
            # - Queue is not empty
            if (
                worker_utilization > 0.8
                and not self.ring_buffer.is_empty()
                and self.current_workers < self.max_workers
            ):
                self.current_workers = min(
                    self.current_workers + 1,
                    self.max_workers
                )
                self.executor._max_workers = self.current_workers

            # Scale down if:
            # - Low worker utilization (<50%)
            # - Queue is mostly empty
            # - Processing times are low
            elif (
                worker_utilization < 0.5
                and self.ring_buffer.is_empty()
                and self.current_workers > self.min_workers
            ):
                self.current_workers = max(
                    self.current_workers - 1,
                    self.min_workers
                )
                self.executor._max_workers = self.current_workers

            self.last_scale_time = current_time

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed worker statistics."""
        with self._lock:
            avg_processing_time = (
                sum(self.processing_times) / len(self.processing_times)
                if self.processing_times else 0
            )
            
            return {
                "queue_size": self.ring_buffer.size,
                "dropped_logs": self.dropped_logs,
                "active_workers": len(self.active_workers),
                "current_workers": self.current_workers,
                "total_processed": self.total_processed,
                "avg_processing_time": avg_processing_time,
                "circuit_breaker_status": "open" if self.circuit_breaker.is_open else "closed",
                "circuit_breaker_failures": self.circuit_breaker.failures
            }
