"""Example demonstrating MS SQL Server logging with SkyArcLog."""

import os
import sys
import time
import uuid
import random
from datetime import datetime
from skyarclog.logger import SkyArcLogger

def simulate_application_events(logger):
    """Simulate application events for SQL logging."""
    event_types = [
        ("user_login", "User authentication"),
        ("order_placed", "E-commerce order"),
        ("payment_processed", "Payment transaction"),
        ("inventory_updated", "Inventory management")
    ]
    
    for i in range(20):
        # Select random event type
        event_type, event_category = random.choice(event_types)
        event_id = str(uuid.uuid4())
        user_id = f"user_{random.randint(1000, 9999)}"
        
        try:
            # Log event start
            logger.info(
                f"Processing {event_type}",
                event_id=event_id,
                event_type=event_type,
                event_category=event_category,
                user_id=user_id,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Simulate processing
            time.sleep(random.uniform(0.1, 0.3))
            
            # Simulate random failures
            if random.random() < 0.15:
                raise ValueError(f"Failed to process {event_type}")
            
            # Log successful event
            logger.info(
                f"{event_type} completed successfully",
                event_id=event_id,
                event_type=event_type,
                user_id=user_id,
                status="success",
                processing_time=random.uniform(100, 300)
            )
            
        except Exception as e:
            # Log failed event
            logger.error(
                f"{event_type} failed",
                event_id=event_id,
                event_type=event_type,
                user_id=user_id,
                status="failed",
                error_type=type(e).__name__,
                error_message=str(e)
            )

def simulate_system_metrics(logger):
    """Simulate system metrics for SQL logging."""
    for i in range(10):
        # CPU metrics
        logger.info(
            "System CPU metrics",
            metric_type="cpu",
            cpu_percent=random.uniform(20, 80),
            process_count=random.randint(50, 200),
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Memory metrics
        total_memory = 16384  # 16GB in MB
        used_memory = random.uniform(4096, 12288)
        logger.info(
            "System memory metrics",
            metric_type="memory",
            total_mb=total_memory,
            used_mb=used_memory,
            free_mb=total_memory - used_memory,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Disk metrics
        logger.info(
            "System disk metrics",
            metric_type="disk",
            disk_read_mb=random.uniform(10, 50),
            disk_write_mb=random.uniform(5, 30),
            iops=random.randint(100, 1000),
            timestamp=datetime.utcnow().isoformat()
        )
        
        time.sleep(1)

def simulate_audit_logs(logger):
    """Simulate audit logs for compliance tracking."""
    audit_actions = [
        ("user_permission_change", "Security"),
        ("data_export", "Data Access"),
        ("config_update", "System Config"),
        ("api_key_rotation", "Security")
    ]
    
    for i in range(15):
        # Select random audit action
        action, category = random.choice(audit_actions)
        admin_user = f"admin_{random.randint(100, 999)}"
        
        # Log audit event
        logger.info(
            f"Audit: {action}",
            audit_id=str(uuid.uuid4()),
            action=action,
            category=category,
            admin_user=admin_user,
            ip_address="10.0.0." + str(random.randint(1, 255)),
            timestamp=datetime.utcnow().isoformat(),
            affected_resource=f"resource_{random.randint(1, 100)}",
            change_details={
                "before": {"status": "old_value"},
                "after": {"status": "new_value"}
            }
        )
        
        time.sleep(random.uniform(0.2, 0.5))

def main():
    """Run MS SQL logging example."""
    # Get the absolute path to the configuration file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'skyarclog_logging.json')

    # Initialize logger with configuration
    logger = SkyArcLogger(config_path)
    
    try:
        print("\n=== Phase 1: Application Event Logging ===")
        print("(Simulating various application events)")
        simulate_application_events(logger)
        
        print("\n=== Phase 2: System Metrics Logging ===")
        print("(Recording system performance metrics)")
        simulate_system_metrics(logger)
        
        print("\n=== Phase 3: Audit Logging ===")
        print("(Generating compliance audit logs)")
        simulate_audit_logs(logger)
        
        # Log final summary
        logger.info(
            "Example completed",
            timestamp=datetime.utcnow().isoformat(),
            phases_completed=[
                "application_events",
                "system_metrics",
                "audit_logs"
            ]
        )
    
    finally:
        # Ensure all logs are written to SQL
        logger.close()

if __name__ == "__main__":
    main()
