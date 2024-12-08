"""Formatter registration and management for SkyArcLog."""

from typing import Dict, Type
from .base_formatter import BaseFormatter
from .json_formatter import JsonFormatter
from .sql_formatter import SqlFormatter
from .protobuf_formatter import ProtobufFormatter

# Global registry of formatters
_formatters: Dict[str, Type[BaseFormatter]] = {}

def register_formatter(name: str, formatter_class: Type[BaseFormatter]) -> None:
    """Register a formatter class.
    
    Args:
        name: Name to register the formatter under
        formatter_class: The formatter class to register
    """
    _formatters[name] = formatter_class

def get_formatter(name: str) -> Type[BaseFormatter]:
    """Get a formatter class by name.
    
    Args:
        name: Name of the formatter to get
        
    Returns:
        The formatter class
        
    Raises:
        KeyError: If formatter not found
    """
    if name not in _formatters:
        raise KeyError(f"Formatter '{name}' not found")
    return _formatters[name]

def create_formatter(name: str, config: dict) -> BaseFormatter:
    """Create a formatter instance.
    
    Args:
        name: Name of the formatter to create
        config: Configuration for the formatter
        
    Returns:
        Configured formatter instance
    """
    formatter_class = get_formatter(name)
    formatter = formatter_class(**config)  # Update to support new configuration approach
    return formatter

# Register built-in formatters
register_formatter('json', JsonFormatter)
register_formatter('sql', SqlFormatter)
register_formatter('protobuf', ProtobufFormatter)

# Export key functions and classes
__all__ = [
    'register_formatter', 
    'get_formatter', 
    'create_formatter',
    'BaseFormatter',
    'JsonFormatter',
    'SqlFormatter',
    'ProtobufFormatter'
]
