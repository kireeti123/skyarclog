"""
Example showing how to use custom configuration with skyarclog.
"""

import logging
import os
from skyarclog import setup_logging
from skyarclog.config import default_config

def get_custom_config():
    # Start with the default configuration
    config = default_config.DEFAULT_CONFIG.copy()
    
    # Customize the configuration
    config['disable_existing_loggers'] = False  # Enable existing loggers
    
    # Add a new file handler for errors only
    config['handlers']['error_file'] = {
        'class': 'logging.FileHandler',
        'level': 'ERROR',
        'formatter': 'detailed',
        'filename': os.path.join(os.getcwd(), 'error.log'),
        'mode': 'a'
    }
    
    # Add a new logger that uses the error file
    config['loggers']['error_logger'] = {
        'handlers': ['error_file'],
        'level': 'ERROR',
        'propagate': False
    }
    
    return config

def main():
    # Get custom configuration
    custom_config = get_custom_config()
    
    # Setup logging with custom configuration
    setup_logging(config=custom_config)
    
    # Get loggers
    log = logging.getLogger(__name__)
    error_log = logging.getLogger('error_logger')
    
    # Regular logging
    log.info("Application started")
    log.debug("Debug message")
    
    # Error logging (will go to both regular log and error log)
    try:
        raise ValueError("Example error")
    except Exception as e:
        error_log.exception("An error occurred", extra={
            "error_type": type(e).__name__
        })

if __name__ == "__main__":
    main()
