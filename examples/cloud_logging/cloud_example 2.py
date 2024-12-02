"""
Cloud logging example using Azure, AWS, and GCP listeners.
"""

from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import (
    AzureAppInsightsListener,
    AWSCloudWatchListener,
    GCPStackdriverListener
)

def setup_logging():
    # Get log manager instance
    log_manager = LogManager.get_instance()
    
    # Add JSON formatter (required for cloud services)
    log_manager.add_formatter(JSONFormatter())
    
    # Add Azure Application Insights listener
    azure_listener = AzureAppInsightsListener(
        connection_string="InstrumentationKey=your-key-here",
        service_name="MyService",
        attributes={
            "environment": "production",
            "region": "us-west"
        }
    )
    log_manager.add_listener(azure_listener)
    
    # Add AWS CloudWatch listener
    aws_listener = AWSCloudWatchListener(
        region="us-west-2",
        log_group="my-application",
        log_stream="production",
        aws_access_key_id="your-access-key",
        aws_secret_access_key="your-secret-key"
    )
    log_manager.add_listener(aws_listener)
    
    # Add Google Cloud Logging listener
    gcp_listener = GCPStackdriverListener(
        project_id="your-project-id",
        log_name="application-logs",
        credentials_file="path/to/credentials.json",
        resource={
            "type": "gce_instance",
            "labels": {
                "instance_id": "my-instance",
                "zone": "us-central1-a"
            }
        }
    )
    log_manager.add_listener(gcp_listener)
    
    return log_manager

def main():
    # Setup logging
    logger = setup_logging()
    
    # Log application events
    logger.info("Application started", {
        "version": "2.0.0",
        "environment": "production",
        "region": "us-west"
    })
    
    # Log user activity
    logger.info("User action", {
        "user_id": "user123",
        "action": "checkout",
        "cart_value": 159.99,
        "items": 3
    })
    
    # Log performance metrics
    logger.warning("High latency detected", {
        "endpoint": "/api/products",
        "latency_ms": 1500,
        "threshold_ms": 1000,
        "concurrent_users": 1000
    })
    
    # Log security events
    logger.error("Authentication failed", {
        "user_id": "user456",
        "ip_address": "203.0.113.1",
        "attempt_count": 5,
        "security_alert": True
    })
    
    # Log critical system events
    logger.critical("Service degradation", {
        "service": "payment_processor",
        "error_rate": 15.5,
        "affected_regions": ["us-west", "us-east"],
        "impact_level": "high"
    })
    
    # Demonstrate structured logging with trace context
    with logger.trace_context(
        operation_name="process_order",
        correlation_id="order_789"
    ):
        logger.info("Processing order", {
            "order_id": "789",
            "customer_id": "cust_123",
            "order_value": 299.99
        })
        
        # Simulating a sub-operation
        with logger.trace_context(
            operation_name="payment_processing",
            parent_operation="process_order"
        ):
            logger.info("Processing payment", {
                "payment_provider": "stripe",
                "amount": 299.99,
                "currency": "USD"
            })

if __name__ == "__main__":
    main()
