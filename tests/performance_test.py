"""
Performance test suite for SkyArcLog's async worker implementation.
Tests various scenarios and measures performance metrics.
"""

import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add parent directory to path to import our logging package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advanced_logging import LogManager
from advanced_logging.async_worker import AsyncWorker
from advanced_logging.listeners import FileListener, ConsoleListener
from advanced_logging.formatters import JSONFormatter

class PerformanceTest:
    def __init__(self):
        self.log_manager = LogManager.get_instance()
        self.test_file = "perf_test.log"
        self.latencies = []
        self.start_time = None
        self.end_time = None
        
    def setup(self, num_workers=4, queue_size=10000, batch_size=1000):
        """Setup the logging infrastructure with specified parameters."""
        # Create async worker with optimized settings
        worker = AsyncWorker(
            num_workers=num_workers,
            queue_size=queue_size,
            batch_size=batch_size,
            max_wait_time=0.1,
            min_workers=2,
            max_workers=8
        )
        
        # Configure log manager
        self.log_manager.reset()  # Clear any existing configuration
        self.log_manager.set_async_worker(worker)
        self.log_manager.add_formatter(JSONFormatter())
        self.log_manager.add_listener(FileListener(self.test_file))
        self.log_manager.add_listener(ConsoleListener())
        
    def cleanup(self):
        """Cleanup test artifacts."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
    def measure_latency(self, num_messages=10000):
        """Measure latency for logging operations."""
        self.latencies = []
        
        for i in range(num_messages):
            start = time.perf_counter()
            self.log_manager.info(f"Test message {i}", extra={"test_id": i})
            end = time.perf_counter()
            self.latencies.append((end - start) * 1000)  # Convert to milliseconds
            
    def measure_throughput(self, num_messages=100000, num_threads=4):
        """Measure throughput with concurrent logging."""
        messages_per_thread = num_messages // num_threads
        self.start_time = time.perf_counter()
        
        def log_batch(thread_id):
            for i in range(messages_per_thread):
                self.log_manager.info(
                    f"Thread {thread_id} message {i}",
                    extra={"thread_id": thread_id, "msg_id": i}
                )
                
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(log_batch, i) 
                for i in range(num_threads)
            ]
            for future in futures:
                future.result()
                
        self.end_time = time.perf_counter()
        
    def run_stress_test(self, duration=10):
        """Run a stress test for specified duration."""
        stop_event = threading.Event()
        message_count = 0
        
        def stress_logger():
            nonlocal message_count
            while not stop_event.is_set():
                self.log_manager.info(
                    "Stress test message",
                    extra={"timestamp": time.time()}
                )
                message_count += 1
                
        threads = [
            threading.Thread(target=stress_logger)
            for _ in range(4)
        ]
        
        # Start stress test
        for thread in threads:
            thread.start()
            
        # Run for specified duration
        time.sleep(duration)
        stop_event.set()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
            
        return message_count
        
    def print_results(self, test_name, message_count):
        """Print performance test results."""
        print(f"\n=== {test_name} Results ===")
        
        if self.latencies:
            avg_latency = statistics.mean(self.latencies)
            p95_latency = statistics.quantiles(self.latencies, n=20)[18]  # 95th percentile
            p99_latency = statistics.quantiles(self.latencies, n=100)[98]  # 99th percentile
            
            print(f"Average Latency: {avg_latency:.3f}ms")
            print(f"95th Percentile Latency: {p95_latency:.3f}ms")
            print(f"99th Percentile Latency: {p99_latency:.3f}ms")
            
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            throughput = message_count / duration
            print(f"Total Duration: {duration:.2f}s")
            print(f"Throughput: {throughput:.2f} messages/second")
            
        # Get worker stats
        stats = self.log_manager.async_worker.get_stats()
        print("\nWorker Statistics:")
        print(f"Active Workers: {stats['active_workers']}")
        print(f"Current Workers: {stats['current_workers']}")
        print(f"Dropped Logs: {stats['dropped_logs']}")
        print(f"Total Processed: {stats['total_processed']}")
        print(f"Average Processing Time: {stats['avg_processing_time']:.3f}s")
        print(f"Circuit Breaker Status: {stats['circuit_breaker_status']}")

def main():
    """Run all performance tests."""
    test = PerformanceTest()
    
    # Test 1: Latency Test
    print("\nRunning Latency Test...")
    test.setup(num_workers=4, queue_size=10000, batch_size=1000)
    test.measure_latency(num_messages=10000)
    test.print_results("Latency Test", 10000)
    test.cleanup()
    
    # Test 2: Throughput Test
    print("\nRunning Throughput Test...")
    test.setup(num_workers=4, queue_size=20000, batch_size=2000)
    test.measure_throughput(num_messages=100000, num_threads=4)
    test.print_results("Throughput Test", 100000)
    test.cleanup()
    
    # Test 3: Stress Test
    print("\nRunning Stress Test...")
    test.setup(num_workers=8, queue_size=50000, batch_size=5000)
    message_count = test.run_stress_test(duration=10)
    test.print_results("Stress Test", message_count)
    test.cleanup()

if __name__ == "__main__":
    main()
