"""Example demonstrating console logging with memory buffer and queue processing."""

import os
import sys
import time
import random
from skyarclog.logger import SkyArcLogger

def simulate_normal_traffic(logger):
    """Simulate normal application traffic with various log levels."""
    for i in range(10):
        # Simulate some work
        time.sleep(0.1)
        
        # Log different types of events
        logger.debug(f"Processing item {i}", item_id=i, component="processor")
        logger.info(f"Item {i} processed successfully", duration=random.uniform(0.1, 0.5))
        
        # Simulate occasional warnings
        if i % 3 == 0:
            logger.warning(
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
        logger.error(
            "System error occurred",
            error_type=type(e).__name__,
            error_message=str(e),
            severity="high"
        )

def simulate_batch_processing(logger):
    """Simulate batch processing with multiple log messages."""
    batch_size = 5
    for batch in range(3):
        logger.info(f"Starting batch {batch}", batch_id=batch)
        
        for i in range(batch_size):
            # Simulate processing items in a batch
            logger.debug(
                f"Processing batch item {i}",
                batch_id=batch,
                item_id=i,
                status="in_progress"
            )
            
            # Simulate occasional processing delays
            if i % 2 == 0:
                logger.warning(
                    "Item processing delayed", 
                    batch_id=batch, 
                    item_id=i, 
                    delay=random.uniform(0.1, 0.3)
                )
        
        logger.info(f"Completed batch {batch}", batch_id=batch, items_processed=batch_size, duration=random.uniform(1.0, 2.0))

def main():
    """Run console logging example with memory buffer and queue processing."""
    # Get the absolute path to the configuration file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "skyarclog_logging.json")
    
    # Initialize logger with configuration path
    logger = SkyArcLogger(config_path)
    
    print("\n=== Simulating normal application traffic ===")
    simulate_normal_traffic(logger)
    
    print("\n=== Simulating error condition ===")
    simulate_error_condition(logger)
    
    print("\n=== Simulating batch processing ===")
    simulate_batch_processing(logger)
    
    print("\n=== Waiting for queue to process remaining messages ===")
    time.sleep(1)  # Give time for any async logging to complete

if __name__ == "__main__":
    main()
