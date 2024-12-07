"""Example demonstrating Azure Blob Storage logging with SkyArcLog."""

import os
import sys
import time
import uuid
import random
from datetime import datetime
from skyarclog.logger import SkyArcLogger

def simulate_application_logs(logger):
    """Simulate application logs that will be stored in Azure Blob."""
    session_id = str(uuid.uuid4())
    
    for i in range(20):
        # Simulate user activity
        user_id = f"user_{random.randint(1000, 9999)}"
        
        # Log various activities
        logger.info(
            f"User {user_id} started activity {i}",
            session_id=session_id,
            user_id=user_id,
            activity_id=i,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Simulate some processing time
        time.sleep(0.2)
        
        # Log completion with random outcome
        success = random.random() > 0.2
        if success:
            logger.info(
                f"Activity {i} completed successfully",
                session_id=session_id,
                user_id=user_id,
                activity_id=i,
                duration=random.uniform(0.1, 0.5)
            )
        else:
            logger.error(
                f"Activity {i} failed",
                session_id=session_id,
                user_id=user_id,
                activity_id=i,
                error_code=random.randint(400, 500)
            )

def simulate_batch_processing(logger):
    """Simulate batch processing logs."""
    batch_id = str(uuid.uuid4())
    total_records = 100
    
    logger.info(
        "Starting batch processing",
        batch_id=batch_id,
        total_records=total_records,
        start_time=datetime.utcnow().isoformat()
    )
    
    processed = 0
    failed = 0
    
    for i in range(total_records):
        try:
            if random.random() < 0.1:
                raise ValueError(f"Processing error for record {i}")
            
            logger.debug(
                f"Processing record {i}",
                batch_id=batch_id,
                record_id=i
            )
            processed += 1
            
        except Exception as e:
            logger.error(
                "Record processing failed",
                batch_id=batch_id,
                record_id=i,
                error=str(e)
            )
            failed += 1
        
        # Progress update every 20 records
        if (i + 1) % 20 == 0:
            logger.info(
                "Batch processing progress",
                batch_id=batch_id,
                processed=processed,
                failed=failed,
                progress=f"{(i+1)/total_records*100:.1f}%"
            )
    
    logger.info(
        "Batch processing completed",
        batch_id=batch_id,
        total_processed=processed,
        total_failed=failed,
        end_time=datetime.utcnow().isoformat()
    )

def main():
    """Run Azure Blob logging example."""
    # Get the absolute path to the configuration file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'skyarclog_logging.json')

    # Initialize logger with configuration
    logger = SkyArcLogger(config_path)
    
    try:
        print("\n=== Phase 1: Application Activity Logging ===")
        print("(Simulating user activities with session tracking)")
        simulate_application_logs(logger)
        
        print("\n=== Phase 2: Batch Processing Logs ===")
        print("(Simulating batch job with progress tracking)")
        simulate_batch_processing(logger)
        
        # Log final summary
        logger.info(
            "Example completed",
            timestamp=datetime.utcnow().isoformat(),
            phases_completed=["application_logs", "batch_processing"]
        )
    
    finally:
        # Ensure all logs are flushed to Azure Blob
        logger.close()

if __name__ == "__main__":
    main()
