"""Example demonstrating asynchronous queue logging with SkyArcLog."""

import os
import sys
import time
import random
import threading
from skyarclog.logger import SkyArcLogger

def simulate_high_volume_traffic(logger):
    """Simulate high volume traffic to demonstrate queue processing."""
    for batch in range(5):
        print(f"\nSending batch {batch} of messages...")
        
        # Send burst of messages
        for i in range(50):
            logger.info(
                f"Processing message {i} in batch {batch}",
                batch_id=batch,
                message_id=i,
                timestamp=time.time()
            )
        
        # Simulate some processing time
        time.sleep(0.5)
        
        # Add some warnings
        for i in range(3):
            logger.warning(
                f"Slow processing detected in batch {batch}",
                batch_id=batch,
                warning_id=i,
                processing_time=random.uniform(1.0, 2.0)
            )

def simulate_worker_failures(logger):
    """Simulate conditions that might cause worker failures."""
    for i in range(10):
        try:
            if random.random() < 0.3:
                # Simulate processing error
                raise ValueError(f"Processing error in message {i}")
            
            logger.info(
                f"Processing message {i}",
                message_id=i,
                status="success"
            )
        except Exception as e:
            logger.error(
                "Message processing failed",
                message_id=i,
                error_type=type(e).__name__,
                error_message=str(e)
            )
        
        # Small delay between messages
        time.sleep(0.1)

def monitor_queue_stats():
    """Simulate monitoring queue statistics."""
    stats = {
        'processed': 0,
        'failed': 0,
        'retried': 0
    }
    
    while True:
        # In a real implementation, we would get these from the queue listener
        stats['processed'] += random.randint(10, 20)
        stats['failed'] += random.randint(0, 2)
        stats['retried'] += random.randint(0, 1)
        
        print(f"\nQueue Stats: {stats}")
        time.sleep(1)

def main():
    """Run queue logging example."""
    # Get the absolute path to the configuration file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'skyarclog_logging.json')

    # Initialize logger with configuration
    logger = SkyArcLogger(config_path)
    
    try:
        # Start queue monitoring in background
        monitor_thread = threading.Thread(target=monitor_queue_stats)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n=== Phase 1: High Volume Message Processing ===")
        print("(Messages will be processed asynchronously by worker threads)")
        simulate_high_volume_traffic(logger)
        
        print("\n=== Phase 2: Simulating Worker Failures ===")
        print("(Some messages will fail and trigger retries)")
        simulate_worker_failures(logger)
        
        print("\n=== Phase 3: Final Messages ===")
        logger.critical(
            "Queue test completed",
            total_batches=5,
            messages_per_batch=50,
            simulated_failures=True
        )
        
        # Wait for queue to process remaining messages
        print("\n=== Waiting for queue to process remaining messages ===")
        time.sleep(5)
    
    finally:
        # Clean up and ensure all messages are processed
        logger.close()

if __name__ == "__main__":
    main()
