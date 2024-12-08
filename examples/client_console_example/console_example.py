import sys
import os
import json
import logging

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.skyarclog.logger import SkyArcLogger

def main():
    # Load configuration from JSON file
    config_path = os.path.join(os.path.dirname(__file__), 'skyarclog_logging_new.json')
    
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON in configuration file: {config_path}")
        return

    # Initialize SkyArcLogger with the configuration
    logger = SkyArcLogger(config)

    # Demonstrate logging at different levels
    logger.debug("This is a debug message")
    logger.info("This is an informational message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Log with additional context
    logger.info("User login", extra={
        "username": "johndoe",
        "ip_address": "192.168.1.100"
    })

    # Log an exception
    try:
        1 / 0  # Intentional division by zero
    except ZeroDivisionError as e:
        logger.exception("An error occurred", exc_info=e)

if __name__ == "__main__":
    main()
