"""SkyArcLog package."""

# Use lazy imports to prevent circular dependencies
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
        from .logger import log
        return log
    elif name == 'configure':
        from .logger import configure
        return configure
    elif name in ['debug', 'info', 'warning', 'error', 'critical']:
        from .logger import debug, info, warning, error, critical
        
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
