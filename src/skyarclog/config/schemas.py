"""Configuration schemas for SkyArcLog."""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ListenerSchema:
    """Base schema for listener configuration."""
    required_fields: Dict[str, Any]
    optional_fields: Dict[str, Any]


# Schema definitions for different listener types
LISTENER_SCHEMAS = {
    'azure_appinsights': ListenerSchema(
        required_fields={
            'instrumentation_key': str
        },
        optional_fields={
            'enable_local_storage': bool,
            'max_batch_size': int,
            'max_batch_interval': int
        }
    ),
    'azure_blob': ListenerSchema(
        required_fields={
            'connection_string': str,
            'container_name': str
        },
        optional_fields={
            'blob_name_prefix': str,
            'max_connections': int,
            'retry_total': int,
            'retry_backoff': float
        }
    ),
    'file': ListenerSchema(
        required_fields={
            'path': str
        },
        optional_fields={
            'max_bytes': int,
            'backup_count': int,
            'encoding': str,
            'delay': bool
        }
    )
}


def validate_listener_config(listener_type: str, config: Dict[str, Any]) -> None:
    """Validate listener configuration against its schema.
    
    Args:
        listener_type: Type of listener
        config: Configuration to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    if listener_type not in LISTENER_SCHEMAS:
        raise ValueError(f"Unknown listener type: {listener_type}")
    
    schema = LISTENER_SCHEMAS[listener_type]
    
    # Check required fields
    for field, field_type in schema.required_fields.items():
        if field not in config:
            raise ValueError(f"Missing required field '{field}' for {listener_type} listener")
        if not isinstance(config[field], field_type):
            raise ValueError(
                f"Invalid type for field '{field}' in {listener_type} listener. "
                f"Expected {field_type.__name__}, got {type(config[field]).__name__}"
            )
    
    # Validate optional fields if present
    for field, value in config.items():
        if field in schema.optional_fields:
            field_type = schema.optional_fields[field]
            if not isinstance(value, field_type):
                raise ValueError(
                    f"Invalid type for optional field '{field}' in {listener_type} listener. "
                    f"Expected {field_type.__name__}, got {type(value).__name__}"
                )
        elif field not in schema.required_fields:
            raise ValueError(f"Unknown field '{field}' for {listener_type} listener")
