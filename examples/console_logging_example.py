"""
Example demonstrating console logging with SkyArcLog.
"""

from skyarclog import logger
import os

def main():
    # Get the path to the configuration file
    current_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(current_dir, 'src', 'skyarclog', 'skyarclog_logging.json')
    
    # Initialize the logger with the configuration file
    logger._ensure_logger()  # Ensure the logger is configured
    
    # Log messages at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Log with extra context
    logger.info(
        "Processing user request",
        extra={
            "user_id": "12345",
            "request_id": "abc-123",
            "ip_address": "192.168.1.1"
        }
    )
    
    # Log an exception
    try:
        result = 1 / 0
    except Exception as e:
        logger.error(
            "Division by zero error",
            extra={
                "operation": "division",
                "error_type": type(e).__name__
            },
            exc_info=True
        )

if __name__ == "__main__":
    main()
