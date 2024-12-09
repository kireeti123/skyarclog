"""Configuration schemas for SkyArcLog."""

from typing import Dict, Any
import json


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


# Load listener schemas from JSON file
with open('listener_schemas.json') as f:
    LISTENER_SCHEMAS = json.load(f)

# Load formatter schemas from JSON file
with open('formatter_schemas.json') as f:
    FORMATTER_SCHEMAS = json.load(f)


def validate_listener_config(listener_type: str, config: Dict[str, Any]) -> None:
    """Validate listener configuration against its schema."""
    schema = LISTENER_SCHEMAS.get(listener_type)
    if not schema:
        raise ValueError(f"No schema found for listener type '{listener_type}'")
    
    # Validate required fields
    for field, expected_type in schema['required_fields'].items():
        if field not in config:
            raise ValueError(f"Missing required field '{field}' for {listener_type} listener")
        if not isinstance(config[field], expected_type):
            raise ValueError(f"Invalid type for field '{field}' in {listener_type} listener")
    
    # Validate optional fields
    for field, expected_type in schema['optional_fields'].items():
        if field in config and not isinstance(config[field], expected_type):
            raise ValueError(f"Invalid type for optional field '{field}' in {listener_type} listener")


def validate_formatter_config(formatter_type: str, config: Dict[str, Any]) -> None:
    """Validate formatter configuration against its schema."""
    schema = FORMATTER_SCHEMAS.get(formatter_type)
    if not schema:
        raise ValueError(f"No schema found for formatter type '{formatter_type}'")
    
    # Validate required fields
    for field, expected_type in schema['required_fields'].items():
        if field not in config:
            raise ValueError(f"Missing required field '{field}' for {formatter_type} formatter")
        if not isinstance(config[field], expected_type):
            raise ValueError(f"Invalid type for field '{field}' in {formatter_type} formatter")
    
    # Validate optional fields
    for field, expected_type in schema['optional_fields'].items():
        if field in config and not isinstance(config[field], expected_type):
            raise ValueError(f"Invalid type for optional field '{field}' in {formatter_type} formatter")
