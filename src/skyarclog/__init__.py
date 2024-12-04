"""
SkyArcLog - A comprehensive logging framework with centralized key vault-based connection management.
"""

from .core import setup_logging
from .config import default_config

__version__ = "1.0.0"
__author__ = "Krishna Kireeti Kompella"
__email__ = "kireeti.k.k@gmail.com"

# Export main functions
__all__ = ['setup_logging', 'default_config']
