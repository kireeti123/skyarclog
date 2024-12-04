"""
Example demonstrating the performance benefits of buffered logging.
This example compares regular logging vs buffered logging performance.
"""

import time
import random
from skyarclog import setup_logging
from skyarclog.buffering import LogBuffer, BufferedHandler

def generate_log_data(num_records: int):
    """Generate sample log records."""
    actions = ['login', 'logout', 'purchase', 'view', 'search']
    status_codes = [200, 201, 400, 401, 403, 404, 500]
    
    for _ in range(num_records):
        yield {
            'user_id': f"user_{random.randint(1, 1000)}",
            'action': random.choice(actions),
            'status_code': random.choice(status_codes),
            'response_time': random.uniform(0.1, 2.0),
            'ip_address': f"192.168.1.{random.randint(1, 255)}"
        }

def test_regular_logging(logger, num_records: int):
    """Test regular logging performance."""
    start_time = time.time()
    
    for data in generate_log_data(num_records):
        logger.info("User activity", extra=data)
        
    end_time = time.time()
    return end_time - start_time

def test_buffered_logging(logger, num_records: int):
    """Test buffered logging performance."""
    start_time = time.time()
    
    # Create a log buffer with batch processing
    buffer = LogBuffer(max_batch_size=100, flush_interval=0.5)
    handler = BufferedHandler(buffer=buffer)
    logger.addHandler(handler)
    
    try:
        for data in generate_log_data(num_records):
            logger.info("User activity", extra=data)
    finally:
        # Ensure all logs are flushed
        handler.flush()
        handler.close()
        
    end_time = time.time()
    return end_time - start_time

def main():
    # Setup logging
    logger = setup_logging("performance")
    log = logger.get_logger()
    
    # Test parameters
    num_records = 10000
    
    # Run performance tests
    print(f"\nTesting with {num_records} log records...")
    
    # Test regular logging
    regular_time = test_regular_logging(log, num_records)
    print(f"\nRegular Logging:")
    print(f"Time taken: {regular_time:.2f} seconds")
    print(f"Throughput: {num_records/regular_time:.2f} records/second")
    
    # Test buffered logging
    buffered_time = test_buffered_logging(log, num_records)
    print(f"\nBuffered Logging:")
    print(f"Time taken: {buffered_time:.2f} seconds")
    print(f"Throughput: {num_records/buffered_time:.2f} records/second")
    
    # Calculate improvement
    improvement = (regular_time - buffered_time) / regular_time * 100
    print(f"\nPerformance Improvement: {improvement:.1f}%")

if __name__ == "__main__":
    main()
