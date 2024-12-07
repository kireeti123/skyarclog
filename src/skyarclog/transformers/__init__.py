"""Transformer registration and management for SkyArcLog."""

from typing import Dict, Type
from .base_transformer import BaseTransformer
from .json_transformer import JsonTransformer

# Global registry of transformers
_transformers: Dict[str, Type[BaseTransformer]] = {}

def register_transformer(name: str, transformer_class: Type[BaseTransformer]) -> None:
    """Register a transformer class.
    
    Args:
        name: Name to register the transformer under
        transformer_class: The transformer class to register
    """
    _transformers[name] = transformer_class

def get_transformer(name: str) -> Type[BaseTransformer]:
    """Get a transformer class by name.
    
    Args:
        name: Name of the transformer to get
        
    Returns:
        The transformer class
        
    Raises:
        KeyError: If transformer not found
    """
    if name not in _transformers:
        raise KeyError(f"Transformer '{name}' not found")
    return _transformers[name]

def create_transformer(name: str, config: dict) -> BaseTransformer:
    """Create a transformer instance.
    
    Args:
        name: Name of the transformer to create
        config: Configuration for the transformer
        
    Returns:
        Configured transformer instance
    """
    transformer_class = get_transformer(name)
    transformer = transformer_class()
    transformer.configure(config)
    return transformer

# Register built-in transformers
register_transformer('json', JsonTransformer)
