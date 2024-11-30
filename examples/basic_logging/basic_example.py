"""
Basic logging example using console and file listeners.
"""

import os
from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter, TextFormatter
from advanced_logging.listeners import ConsoleListener, FileListener

def setup_logging():
    # Get log manager instance
    log_manager = LogManager.get_instance()
    
    # Add formatters
    log_manager.add_formatter(JSONFormatter())
    log_manager.add_formatter(TextFormatter())
    
    # Add console listener with colored output
    console_listener = ConsoleListener(colored=True)
    log_manager.add_listener(console_listener)
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Add file listener with rotation
    file_listener = FileListener(
        filepath="logs/app.log",
        rotate=True,
        max_size="10MB",
        backup_count=5
    )
    log_manager.add_listener(file_listener)
    
    return log_manager

def main():
    # Setup logging
    logger = setup_logging()
    
    # Log different levels with context
    logger.info("Application started", {"version": "1.0.0"})
    logger.debug("Debug message", {"detail": "Extra debug info"})
    logger.warning("Warning message", {"warning_code": "W001"})
    logger.error("Error occurred", {
        "error_code": "E001",
        "stack_trace": "..."
    })
    
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.critical("Critical error", {
            "error": str(e),
            "type": "ValueError"
        })

if __name__ == "__main__":
    main()
