"""
Performance test for SkyArcLog demonstrating non-blocking behavior
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List

from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import FileListener, RedisListener

def simulate_work(duration: float = 0.1) -> None:
    """Simulate some CPU-bound work."""
    start = time.time()
    while time.time() - start < duration:
        _ = sum(i * i for i in range(1000))

def log_intensive_task(log_manager: LogManager, num_logs: int) -> float:
    """
    Run a log-intensive task and measure the time it takes.
    
    Args:
        log_manager: The LogManager instance
        num_logs: Number of log messages to generate
        
    Returns:
        float: Time taken in seconds
    """
    start_time = time.time()
    
    for i in range(num_logs):
        log_manager.info(
            f"Log message {i}",
            extra={
                "iteration": i,
                "timestamp": time.time(),
                "thread": threading.current_thread().name
            }
        )
        
    end_time = time.time()
    return end_time - start_time

def main():
    # Initialize logging
    log_manager = LogManager.get_instance()
    log_manager.add_formatter(JSONFormatter())
    log_manager.add_listener(FileListener("performance_test.log"))
    
    # Test parameters
    num_threads = 4
    logs_per_thread = 10000
    
    print("Starting performance test...")
    print(f"Threads: {num_threads}")
    print(f"Logs per thread: {logs_per_thread}")
    print("=" * 50)
    
    # Run logging tasks in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        
        # Start timing
        total_start = time.time()
        
        # Submit logging tasks
        for _ in range(num_threads):
            future = executor.submit(log_intensive_task, log_manager, logs_per_thread)
            futures.append(future)
            
        # Simulate application work while logging happens
        print("Simulating application work...")
        for _ in range(10):
            simulate_work(0.5)  # Simulate 0.5s of work
            print(".", end="", flush=True)
        print("\n")
        
        # Wait for all logging tasks to complete
        times = [f.result() for f in futures]
        
    total_time = time.time() - total_start
    
    # Print results
    print("\nResults:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per thread: {sum(times)/len(times):.2f} seconds")
    print(f"Total logs: {num_threads * logs_per_thread}")
    print(f"Logs per second: {(num_threads * logs_per_thread) / total_time:.2f}")
    
    # Get worker stats
    stats = log_manager.get_stats()
    print("\nWorker Stats:")
    print(f"Queue size: {stats['worker_stats']['queue_size']}")
    print(f"Dropped logs: {stats['worker_stats']['dropped_logs']}")
    print(f"Active workers: {stats['worker_stats']['active_workers']}")
    
    # Clean up
    log_manager.close()

if __name__ == "__main__":
    main()
