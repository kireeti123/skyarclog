"""Configuration schemas for SkyArcLog."""

from typing import Dict, Any
from dataclasses import dataclass


def validate_listener_config(listener_type: str, config: Dict[str, Any], listener_schemas: Dict[str, Any]) -> None:
    """Validate listener configuration against its schema.
    
    Args:
        listener_type: Type of listener
        config: Configuration to validate
        listener_schemas: Schemas for listeners
        
    Raises:
        ValueError: If configuration is invalid
    """
    if listener_type not in ['console', 'file', 'azure_appinsights', 'azure_blob', 'azure_ms_sql', 'memory', 'queue']:
        raise ValueError(f"Unknown listener type: {listener_type}")
    
    schema = listener_schemas.get(listener_type)
    
    # Check required fields
    for field, field_type in schema['required_fields'].items():
        if field not in config:
            raise ValueError(f"Missing required field '{field}' for {listener_type} listener")
        if not isinstance(config[field], field_type):
            raise ValueError(
                f"Invalid type for field '{field}' in {listener_type} listener. "
                f"Expected {field_type.__name__}, got {type(config[field]).__name__}"
            )
    
    # Validate optional fields if present
    for field, value in config.items():
        if field in schema['optional_fields']:
            field_type = schema['optional_fields'][field]
            if not isinstance(value, field_type):
                raise ValueError(
                    f"Invalid type for optional field '{field}' in {listener_type} listener. "
                    f"Expected {field_type.__name__}, got {type(value).__name__}"
                )
        elif field not in schema['required_fields']:
            raise ValueError(f"Unknown field '{field}' for {listener_type} listener")
