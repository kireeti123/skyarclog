"""Formatter registration and management for SkyArcLog."""

from typing import Dict, Type
from .base_formatter import BaseFormatter
from .json_formatter import JsonFormatter
from .sql_formatter import SqlFormatter
from .protobuf_formatter import ProtobufFormatter
from .text_formatter import TextFormatter

# Global registry of formatters
_formatters: Dict[str, Type[BaseFormatter]] = {}

def _format_name_to_type(name: str) -> str:
    """Convert formatter name to its type identifier.
    
    Args:
        name: Base name of the formatter (e.g., 'json', 'sql')
        
    Returns:
        Formatter type identifier (e.g., 'json_formatter')
    """
    return f"{name}_formatter"

def _get_formatter_class_name(name: str) -> str:
    """Convert formatter name to its class name.
    
    Args:
        name: Base name of the formatter (e.g., 'json', 'sql')
        
    Returns:
        Formatter class name (e.g., 'JsonFormatter')
    """
    return f"{name.title()}Formatter"

def register_formatter(name: str, formatter_class: Type[BaseFormatter]) -> None:
    """Register a formatter class.
    
    Args:
        name: Name to register the formatter under
        formatter_class: The formatter class to register
    """
    formatter_type = _format_name_to_type(name)
    _formatters[formatter_type] = formatter_class

def get_formatter(name: str) -> Type[BaseFormatter]:
    """Get a formatter class by name.
    
    Args:
        name: Name of the formatter to get
        
    Returns:
        The formatter class
        
    Raises:
        KeyError: If formatter not found
    """
    formatter_type = _format_name_to_type(name)
    if formatter_type not in _formatters:
        raise KeyError(f"Formatter '{name}' not found")
    return _formatters[formatter_type]

def create_formatter(name: str, config: dict) -> BaseFormatter:
    """Create a formatter instance.
    
    Args:
        name: Name of the formatter to create
        config: Configuration for the formatter
        
    Returns:
        Configured formatter instance
    """
    formatter_class = get_formatter(name)
    return formatter_class(**config)

# Register built-in formatters
for formatter_name in ['json', 'sql', 'protobuf', 'text']:
    # Dynamically get the formatter class from the module
    class_name = _get_formatter_class_name(formatter_name)
    formatter_type = _format_name_to_type(formatter_name)
    # Register the formatter with its type identifier
    register_formatter(formatter_name, globals()[class_name])

# Export key functions and classes
__all__ = [
    'register_formatter',
    'get_formatter',
    'create_formatter',
    'BaseFormatter',
    'JsonFormatter',
    'SqlFormatter',
    'ProtobufFormatter',
    'TextFormatter'
]
