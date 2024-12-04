"""
Example of using skyarclog with Azure integration.

This example demonstrates how to:
1. Configure Azure logging
2. Use Azure Application Insights
3. Store logs in Azure Blob Storage

Requirements:
    pip install skyarclog[azure]
"""
import os
from skyarclog import setup_logging

def main():
    # Setup logging with Azure-enabled configuration
    logger = setup_logging("prod")  # Will use custom_logging_prod.json
    log = logger.get_logger()
    
    # Basic logging examples
    log.info("Application started", extra={
        "version": logger.config["application"]["version"],
        "environment": logger.config["application"].get("environment", "production")
    })
    
    # Log with Azure Application Insights context
    log.info("User logged in", extra={
        "user_id": "12345",
        "location": "US-West",
        "custom_dimensions": {
            "browser": "Chrome",
            "platform": "Windows"
        }
    })
    
    # Log error with exception tracking
    try:
        raise ValueError("Example error")
    except Exception as e:
        log.exception("An error occurred", extra={
            "operation_id": "login-123",
            "correlation_id": "abc-xyz-789",
            "error_type": type(e).__name__
        })

if __name__ == "__main__":
    # Set Azure credentials (in production, use Azure Key Vault)
    os.environ["AZURE_CONNECTION_STRING"] = "your_connection_string"
    os.environ["AZURE_INSTRUMENTATION_KEY"] = "your_instrumentation_key"
    os.environ["AZURE_BLOB_CONNECTION_STRING"] = "your_blob_connection_string"
    
    main()
