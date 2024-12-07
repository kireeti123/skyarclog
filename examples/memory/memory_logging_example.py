"""Example demonstrating memory buffered logging with SkyArcLog."""

import os
import sys
import time
import random
from skyarclog.logger import SkyArcLogger

def simulate_low_priority_traffic(logger):
    """Simulate low priority traffic that gets buffered."""
    for i in range(20):
        # Simulate some work with short delay
        time.sleep(0.05)
        
        # Log debug/info messages that will be buffered
        logger.debug(f"Processing item {i}", item_id=i, component="processor")
        logger.info(f"Item {i} completed", duration=random.uniform(0.1, 0.3))
        
        # Occasional warning
        if i % 5 == 0:
            logger.warning(
                "Processing took longer than expected",
                item_id=i,
                duration=random.uniform(0.5, 1.0)
            )

def simulate_high_priority_event(logger):
    """Simulate high priority event that triggers buffer flush."""
    try:
        # Simulate critical error
        raise ValueError("Critical system error detected")
    except Exception as e:
        logger.error(
            "System error occurred - triggering buffer flush",
            error_type=type(e).__name__,
            error_message=str(e),
            severity="high"
        )

def main():
    """Run memory logging example."""
    # Get the absolute path to the configuration file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'skyarclog_logging.json')

    # Initialize logger with configuration
    logger = SkyArcLogger(config_path)
    
    try:
        print("\n=== Phase 1: Buffering low priority messages ===")
        print("(Debug/Info messages are being buffered, only warnings shown)")
        simulate_low_priority_traffic(logger)
        
        print("\n=== Phase 2: Triggering flush with high priority message ===")
        print("(Error will trigger immediate flush of buffered messages)")
        simulate_high_priority_event(logger)
        
        print("\n=== Phase 3: Demonstrating capacity-based flush ===")
        print("(Sending many messages to trigger capacity flush)")
        for i in range(100):
            logger.info(
                f"Capacity test message {i}",
                test_id=i,
                timestamp=time.time()
            )
        
        print("\n=== Phase 4: Waiting for time-based flush ===")
        print(f"(Waiting for flush interval...)")
        time.sleep(5)  # Wait to see time-based flush
        
        # Final critical message
        logger.critical(
            "Example completed",
            total_messages="120+",
            flush_triggers=["error", "capacity", "time"]
        )
    
    finally:
        # Clean up and ensure all messages are flushed
        logger.close()

if __name__ == "__main__":
    main()
