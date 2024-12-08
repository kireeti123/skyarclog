import os
import time
import logging
from dotenv import load_dotenv
from skyarclog import SkyArcLogger

def main():
    # Load environment variables (ensure you have a .env file with AZURE_STORAGE_CONNECTION_STRING)
    load_dotenv()

    # Validate Azure connection string
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING must be set in .env file")

    # Initialize logger with configuration
    logger = SkyArcLogger(
        config_path='skyarclog_azure_blob.json'
    )

    # Get the root logger to demonstrate different logging levels
    root_logger = logging.getLogger()

    # Demonstrate logging with different levels and extra information
    root_logger.debug("This is a debug message")
    
    for i in range(10):
        root_logger.info(f"Processing item {i}", 
                    extra={
                        'item_number': i,
                        'processing_time': time.time(),
                        'status': 'success'
                    })
        
        if i % 3 == 0:
            root_logger.warning(f"Potential issue with item {i}", 
                           extra={
                               'item_number': i,
                               'warning_type': 'potential_duplicate'
                           })
        
        if i % 5 == 0:
            root_logger.error(f"Error processing item {i}")
        
        time.sleep(0.5)  # Simulate processing time

    # Ensure logs are flushed
    logging.shutdown()

if __name__ == "__main__":
    main()
