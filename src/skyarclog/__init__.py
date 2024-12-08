"""SkyArcLog package."""

# Use lazy imports to prevent circular dependencies
__all__ = [
    'log', 
    'configure', 
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
