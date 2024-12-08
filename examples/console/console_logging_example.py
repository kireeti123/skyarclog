"""Example demonstrating console logging with memory buffer and queue processing."""

import os
import sys
import time
import random
import skyarclog

def simulate_normal_traffic(logger):
    """Simulate normal application traffic with various log levels."""
    for i in range(10):
        # Simulate some work
        time.sleep(0.1)
        
        # Log different types of events
        logger.log('DEBUG', f"Processing item {i}", item_id=i, component="processor")
        logger.log('INFO', f"Item {i} processed successfully", duration=random.uniform(0.1, 0.5))
        
        # Simulate occasional warnings
        if i % 3 == 0:
            logger.log(
                'WARNING', 
                "Processing took longer than expected",
                item_id=i,
                duration=random.uniform(0.5, 1.0)
            )

def simulate_error_condition(logger):
    """Simulate an error condition that triggers immediate flush."""
    try:
        # Simulate a critical error
        raise ValueError("Critical system error detected")
    except Exception as e:
        logger.log(
            'ERROR',
            "System error occurred",
            error_type=type(e).__name__,
            error_message=str(e),
            severity="high"
        )

def simulate_batch_processing(logger):
    """Simulate batch processing with multiple log messages."""
    batch_size = 5
    for batch in range(3):
        logger.log('INFO', f"Starting batch {batch}", batch_id=batch)
        
        for i in range(batch_size):
            # Simulate processing items in a batch
            logger.log(
                'DEBUG',
                f"Processing batch item {i}",
                batch_id=batch,
                item_id=i
            )

def main():
    """Run console logging example with memory buffer and queue processing."""
    # Configure logging (optional, uses default config if not specified)
    skyarclog.configure()
    
    # Create a logger instance
    logger = skyarclog.logger.SkyArcLogger()
    
    print("\n=== Simulating normal application traffic ===")
    simulate_normal_traffic(logger)
    
    print("\n=== Simulating error condition ===")
    simulate_error_condition(logger)
    
    print("\n=== Simulating batch processing ===")
    simulate_batch_processing(logger)
    
    print("\n=== Waiting for queue to process remaining messages ===")
    logger.close()

if __name__ == "__main__":
    main()
