"""Listener registration and management for SkyArcLog."""

from typing import Dict, Type
from .base_listener import BaseListener

# Global registry of listeners
_listeners: Dict[str, Type[BaseListener]] = {}

def _format_name_to_type(name: str) -> str:
    """Convert listener name to its type identifier.
    
    Args:
        name: Base name of the listener (e.g., 'console', 'azure-blob')
        
    Returns:
        Listener type identifier (e.g., 'console_listener', 'azure_blob_listener')
    """
    # Replace hyphens with underscores and add _listener suffix
    return f"{name.replace('-', '_')}_listener"

def _get_listener_class_name(name: str) -> str:
    """Convert listener name to its class name.
    
    Args:
        name: Base name of the listener (e.g., 'console', 'azure-blob')
        
    Returns:
        Listener class name (e.g., 'ConsoleListener', 'AzureBlobListener')
    """
    # Convert hyphenated/underscored names to CamelCase and add Listener suffix
    return ''.join(word.title() for word in name.replace('-', '_').split('_')) + 'Listener'

def register_listener(name: str, listener_class: Type[BaseListener]) -> None:
    """Register a listener class.
    
    Args:
        name: Name to register the listener under
        listener_class: The listener class to register
    """
    listener_type = _format_name_to_type(name)
    _listeners[listener_type] = listener_class

def get_listener(name: str) -> Type[BaseListener]:
    """Get a listener class by name.
    
    Args:
        name: Name of the listener to get
        
    Returns:
        The listener class
        
    Raises:
        KeyError: If listener not found
    """
    listener_type = _format_name_to_type(name)
    if listener_type not in _listeners:
        raise KeyError(f"Listener '{name}' not found")
    return _listeners[listener_type]

def create_listener(name: str, config: dict) -> BaseListener:
    """Create a listener instance.
    
    Args:
        name: Name of the listener to create
        config: Configuration for the listener
        
    Returns:
        Configured listener instance
    """
    listener_class = get_listener(name)
    return listener_class(config)

# Import all built-in listeners
from .console.console_listener import ConsoleListener
from .file_listener import FileListener
from .azure.azure_appinsights_listener import AzureAppinsightsListener
from .azure.azure_blob_listener import AzureBlobListener
from .azure.azure_ms_sql_listener import AzureMsSqlListener
from .memory_listener import MemoryListener
from .queue_listener import QueueListener

# Register built-in listeners
_built_in_listeners = [
    ('console', ConsoleListener),
    ('file', FileListener),
    ('azure-appinsights', AzureAppinsightsListener),
    ('azure-blob', AzureBlobListener),
    ('azure-ms-sql', AzureMsSqlListener),
    ('memory', MemoryListener),
    ('queue', QueueListener)
]

for name, listener_class in _built_in_listeners:
    register_listener(name, listener_class)

# Export key functions and classes
__all__ = [
    'register_listener',
    'get_listener',
    'create_listener',
    'BaseListener',
    'ConsoleListener',
    'FileListener',
    'AzureAppinsightsListener',
    'AzureBlobListener',
    'AzureMsSqlListener',
    'MemoryListener',
    'QueueListener'
]
