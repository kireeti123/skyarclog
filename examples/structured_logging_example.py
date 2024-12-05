"""
Example demonstrating structured logging with skyarclog.
"""
from skyarclog.core import setup_logging, get_logger

def main():
    # Initialize logging system
    setup_logging(env='dev')  # or 'prod' for production settings
    
    # Get different loggers for different components
    root_logger = get_logger()  # Root logger
    app_logger = get_logger('app')  # Main application logger
    api_logger = get_logger('app.api')  # API component logger
    security_logger = get_logger('app.security')  # Security component logger
    audit_logger = get_logger('app.audit')  # Audit logger
    background_logger = get_logger('app.background')  # Background tasks logger

    # Example usage of different loggers
    
    # Root logger - basic system messages
    root_logger.warning("System starting up...")
    
    # Main application logger
    app_logger.info("Application initialized")
    app_logger.debug("Debug mode enabled")
    
    # API logger - includes request tracking
    api_logger.info("API request received", extra={
        'method': 'GET',
        'path': '/api/v1/users',
        'client_ip': '192.168.1.1'
    })
    
    # Security logger - security events
    security_logger.warning("Failed login attempt", extra={
        'username': 'user123',
        'ip_address': '192.168.1.100',
        'attempt_count': 3
    })
    
    # Audit logger - tracking important changes
    audit_logger.info("User profile updated", extra={
        'user_id': '12345',
        'changes': {'email': 'new@example.com'},
        'timestamp': '2023-12-04T12:00:00Z'
    })
    
    # Background tasks logger
    background_logger.debug("Starting background job", extra={
        'job_id': 'job_123',
        'job_type': 'data_cleanup'
    })

if __name__ == '__main__':
    main()
