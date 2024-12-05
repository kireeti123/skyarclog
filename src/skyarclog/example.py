import os
from dotenv import load_dotenv
from logger import SkyArcLogger

# Load environment variables
load_dotenv()

# Initialize the logger
logger = SkyArcLogger()

# Get a named logger
app_logger = logger.get_logger('app')

def main():
    # Log messages at different levels
    app_logger.debug("This is a debug message")
    app_logger.info("This is an info message")
    app_logger.warning("This is a warning message")
    app_logger.error("This is an error message")
    
    # Log with extra context
    extra = {
        'user_id': '12345',
        'transaction_id': 'abc-xyz-789',
        'service': 'payment-processor'
    }
    app_logger.info("Processing payment", extra=extra)
    
    # Log an exception
    try:
        raise ValueError("Invalid amount")
    except Exception as e:
        app_logger.exception("Failed to process payment", extra=extra)

if __name__ == "__main__":
    main()
