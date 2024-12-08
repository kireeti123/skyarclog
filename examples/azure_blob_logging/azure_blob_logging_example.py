"""Azure Blob Storage Logging Example."""

import os
import time
import random
from dotenv import load_dotenv

import skyarclog
from skyarclog import log

def simulate_blob_operations():
    """Simulate various Azure Blob Storage operations."""
    
    # Simulate upload operations
    for i in range(5):
        log.info(
            f"Uploading blob {i}", 
            blob_name=f"blob_{i}.txt", 
            size=random.randint(100, 1000)
        )
        
        # Simulate occasional upload errors
        if i % 3 == 0:
            log.warning(
                f"Potential upload issue with blob {i}",
                blob_name=f"blob_{i}.txt",
                retry_count=1
            )
        
        time.sleep(0.5)  # Simulate processing time

def simulate_blob_download():
    """Simulate blob download operations."""
    
    for i in range(3):
        log.debug(
            f"Downloading blob {i}", 
            blob_name=f"download_blob_{i}.txt"
        )
        
        # Simulate download errors
        if i % 2 == 0:
            log.error(
                f"Download failed for blob {i}",
                blob_name=f"download_blob_{i}.txt",
                error_code="DOWNLOAD_FAILED"
            )
        
        time.sleep(0.3)  # Simulate download time

def main():
    """Run Azure Blob logging example."""
    # Load environment variables
    load_dotenv()

    # Validate Azure connection string
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        log.critical(
            "Azure Storage Connection String is missing",
            error_type="CONFIGURATION_ERROR"
        )
        return

    # Configure logging
    skyarclog.configure()

    print("\n=== Simulating Blob Upload Operations ===")
    simulate_blob_operations()

    print("\n=== Simulating Blob Download Operations ===")
    simulate_blob_download()

if __name__ == "__main__":
    main()
