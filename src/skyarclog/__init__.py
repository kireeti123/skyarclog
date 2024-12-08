"""SkyArcLog package."""

import importlib
import warnings

# Global logger configuration
__all__ = [
    'log', 
    'configure', 
    'debug',
    'info', 
    'warning',
    'error',
    'critical',
    'logger', 
    'config', 
    'core'
]

# Global logger instance
_GLOBAL_LOGGER = None

# Import logger module to ensure all functions are available
from .logger import (
    log, 
    debug, 
    info, 
    warning, 
    error, 
    critical, 
    SkyArcLogger
)

# Explicitly import configure to avoid circular import issues
from .logger import configure as _configure

def configure(config_path=None):
    """
    Wrapper for logger configuration to handle potential import issues.
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        Configured SkyArcLogger instance
    """
    global _GLOBAL_LOGGER
    try:
        _GLOBAL_LOGGER = _configure(config_path)
        return _GLOBAL_LOGGER
    except Exception as e:
        warnings.warn(f"Failed to configure logger: {e}", RuntimeWarning)
        # Fallback to default logger
        _GLOBAL_LOGGER = SkyArcLogger()
        return _GLOBAL_LOGGER

def __getattr__(name):
    """
    Lazily import modules to prevent circular imports.
    
    Args:
        name: Name of the attribute to import
    
    Returns:
        Imported module or function
    """
    global _GLOBAL_LOGGER

    if name == 'log':
        return log
    elif name == 'configure':
        return configure
    elif name in ['debug', 'info', 'warning', 'error', 'critical']:
        # Ensure we have a global logger
        if _GLOBAL_LOGGER is None:
            _GLOBAL_LOGGER = configure()
        
        # Map the function to use the global logger
        func_map = {
            'debug': debug,
            'info': info,
            'warning': warning,
            'error': error,
            'critical': critical
        }
        return func_map[name]
    elif name == 'logger':
        from . import logger
        return logger
    elif name == 'config':
        from . import config_manager as config
        return config
    elif name == 'core':
        from . import core
        return core
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Prevent further imports during initialization
__import__ = None
