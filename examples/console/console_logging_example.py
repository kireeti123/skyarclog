"""Example demonstrating console logging with memory buffer and queue processing."""

import os
import sys
import time
import random
import skyarclog
from skyarclog import log

def simulate_normal_traffic():
    """Simulate normal application traffic with various log levels."""
    for i in range(10):
        # Simulate some work
        time.sleep(0.1)
        
        # Log different types of events
        log.debug(f"Processing item {i}", item_id=i, component="processor")
        log.info(f"Item {i} processed successfully", duration=random.uniform(0.1, 0.5))
        
        # Simulate occasional warnings
        if i % 3 == 0:
            log.warning(
                "Processing took longer than expected",
                item_id=i,
                duration=random.uniform(0.5, 1.0)
            )

def simulate_error_condition():
    """Simulate an error condition that triggers immediate flush."""
    try:
        # Simulate a critical error
        raise ValueError("Critical system error detected")
    except Exception as e:
        log.error(
            "System error occurred",
            error_type=type(e).__name__,
            error_message=str(e),
            severity="high"
        )

def simulate_batch_processing():
    """Simulate batch processing with multiple log messages."""
    batch_size = 5
    for batch in range(3):
        log.info(f"Starting batch {batch}", batch_id=batch)
        
        for i in range(batch_size):
            # Simulate processing items in a batch
            log.debug(
                f"Processing batch item {i}",
                batch_id=batch,
                item_id=i
            )

def main():
    """Run console logging example with memory buffer and queue processing."""
    # Configure logging (optional, uses default config if not specified)
    skyarclog.configure()
    
    print("\n=== Simulating normal application traffic ===")
    simulate_normal_traffic()
    
    print("\n=== Simulating error condition ===")
    simulate_error_condition()
    
    print("\n=== Simulating batch processing ===")
    simulate_batch_processing()
    
    print("\n=== Waiting for queue to process remaining messages ===")

if __name__ == "__main__":
    main()
