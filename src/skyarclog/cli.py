"""
Command-line interface for skyarclog.
"""

import argparse
import logging
from . import setup_logging, default_config, __version__

def main():
    """Main entry point for the skyarclog CLI."""
    parser = argparse.ArgumentParser(
        description="SkyArcLog - Advanced Logging Framework"
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a test log message'
    )
    
    args = parser.parse_args()
    
    if args.test:
        # Setup logging with default configuration
        logger = setup_logging()
        log = logging.getLogger(__name__)
        
        # Log a test message
        log.info("Test log message from SkyArcLog CLI", extra={
            "version": __version__,
            "test": True
        })
        print("Test log message sent successfully!")

if __name__ == '__main__':
    main()
