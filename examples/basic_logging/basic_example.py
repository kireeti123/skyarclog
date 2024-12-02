"""
Basic logging example using skyarclog.
"""

import logging
from skyarclog import setup_logging
from skyarclog.config import default_config

def main():
    # Setup logging with default configuration
    logger = setup_logging()
    
    # Get a logger for this module
    log = logging.getLogger(__name__)
    
    # Log different levels with context
    log.info("Application started", extra={"version": "1.0.0"})
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
