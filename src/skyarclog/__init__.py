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

def __getattr__(name):
    """
    Lazily import modules to prevent circular imports.
    
    Args:
        name: Name of the attribute to import
    
    Returns:
        Imported module or function
    """
    if name == 'log':
        from .logger import log
        return log
    elif name == 'configure':
        from .logger import configure
        return configure
    elif name == 'debug':
        from .logger import debug
        return debug
    elif name == 'info':
        from .logger import info
        return info
    elif name == 'warning':
        from .logger import warning
        return warning
    elif name == 'error':
        from .logger import error
        return error
    elif name == 'critical':
        from .logger import critical
        return critical
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
