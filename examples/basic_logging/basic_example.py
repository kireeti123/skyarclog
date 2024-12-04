"""
Basic logging example using skyarclog with simplified setup.
"""

from skyarclog import setup_logging

def main():
    # Setup logging with environment
    logger = setup_logging("dev")
    
    # Get logger instance (automatically uses application name from config)
    log = logger.get_logger()
    
    # Log different levels with context
    log.info("Application started", extra={
        "version": logger.config["application"]["version"],
        "environment": logger.config["application"].get("environment", "default")
    })
    log.debug("Debug message", extra={"detail": "Extra debug info"})
    log.warning("Warning message", extra={"warning_code": "W001"})
    log.error("Error occurred", extra={
        "error_code": "E001",
        "stack_trace": "..."
    })
    
    try:
        raise ValueError("Example error")
    except Exception as e:
        log.exception("An error occurred", extra={"error_type": type(e).__name__})

if __name__ == "__main__":
    main()
