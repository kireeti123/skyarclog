"""Configuration validation utilities for SkyArcLog."""

from typing import Dict, List, Optional, Union
import logging


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""
    pass


def validate_handler_config(handler_type: str, config: Dict) -> None:
    """Validate handler configuration.
    
    Args:
        handler_type (str): Type of handler being configured
        config (Dict): Handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Validate common handler settings
    _validate_common_settings(config)
    
    # Validate handler-specific settings
    validator = _get_handler_validator(handler_type)
    if validator:
        validator(config)


def _validate_common_settings(config: Dict) -> None:
    """Validate common handler settings.
    
    Args:
        config (Dict): Handler configuration
        
    Raises:
        ConfigValidationError: If common settings are invalid
    """
    # Validate logging level
    if 'level' in config:
        level = config['level'].upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            raise ConfigValidationError(
                f"Invalid logging level: {level}. Must be one of {valid_levels}"
            )

    # Validate formatter settings
    if 'formatter' in config:
        formatter = config['formatter']
        if not isinstance(formatter, dict):
            raise ConfigValidationError("Formatter configuration must be a dictionary")
        
        formatter_type = formatter.get('type', 'json')
        if formatter_type not in ['json', 'string']:
            raise ConfigValidationError(
                f"Invalid formatter type: {formatter_type}. Must be 'json' or 'string'"
            )


def _validate_file_handler(config: Dict) -> None:
    """Validate file handler configuration.
    
    Args:
        config (Dict): File handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    if 'filename' not in config:
        raise ConfigValidationError("File handler requires 'filename' parameter")
    
    if 'rotation' in config:
        rotation = config['rotation']
        if not isinstance(rotation, dict):
            raise ConfigValidationError("Rotation configuration must be a dictionary")
        
        if 'max_bytes' in rotation and not isinstance(rotation['max_bytes'], int):
            raise ConfigValidationError("max_bytes must be an integer")
        
        if 'backup_count' in rotation and not isinstance(rotation['backup_count'], int):
            raise ConfigValidationError("backup_count must be an integer")


def _validate_memory_handler(config: Dict) -> None:
    """Validate memory handler configuration.
    
    Args:
        config (Dict): Memory handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    if 'capacity' in config and not isinstance(config['capacity'], int):
        raise ConfigValidationError("Memory handler capacity must be an integer")
    
    if 'flush_interval' in config:
        interval = config['flush_interval']
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise ConfigValidationError(
                "Memory handler flush_interval must be a positive number"
            )


def _validate_queue_handler(config: Dict) -> None:
    """Validate queue handler configuration.
    
    Args:
        config (Dict): Queue handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    if 'batch_size' in config:
        batch_size = config['batch_size']
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ConfigValidationError(
                "Queue handler batch_size must be a positive integer"
            )
    
    if 'target_handlers' not in config:
        raise ConfigValidationError(
            "Queue handler requires 'target_handlers' configuration"
        )
    
    if not isinstance(config['target_handlers'], list):
        raise ConfigValidationError("target_handlers must be a list")


def _validate_azure_blob_handler(config: Dict) -> None:
    """Validate Azure Blob handler configuration.
    
    Args:
        config (Dict): Azure Blob handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    required = ['container_connection_string', 'container_name']
    for param in required:
        if param not in config:
            raise ConfigValidationError(
                f"Azure Blob handler requires '{param}' parameter"
            )


def _validate_azure_appinsights_handler(config: Dict) -> None:
    """Validate Azure Application Insights handler configuration.
    
    Args:
        config (Dict): Azure Application Insights handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    if 'instrumentation_key' not in config:
        raise ConfigValidationError(
            "Azure Application Insights handler requires 'instrumentation_key'"
        )
    
    if 'buffer' in config:
        buffer = config['buffer']
        if not isinstance(buffer, dict):
            raise ConfigValidationError("Buffer configuration must be a dictionary")
        
        if 'max_size' in buffer and not isinstance(buffer['max_size'], int):
            raise ConfigValidationError("Buffer max_size must be an integer")
        
        if 'queue_size' in buffer and not isinstance(buffer['queue_size'], int):
            raise ConfigValidationError("Buffer queue_size must be an integer")


def _validate_azure_sql_handler(config: Dict) -> None:
    """Validate Azure SQL handler configuration.
    
    Args:
        config (Dict): Azure SQL handler configuration
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    required = ['connection_string', 'table_name']
    for param in required:
        if param not in config:
            raise ConfigValidationError(
                f"Azure SQL handler requires '{param}' parameter"
            )


def _get_handler_validator(handler_type: str):
    """Get the validator function for a handler type.
    
    Args:
        handler_type (str): Type of handler
        
    Returns:
        Optional[callable]: Validator function for the handler type
    """
    validators = {
        'file': _validate_file_handler,
        'memory': _validate_memory_handler,
        'queue': _validate_queue_handler,
        'azure-blob': _validate_azure_blob_handler,
        'azure-appinsights': _validate_azure_appinsights_handler,
        'azure-sql': _validate_azure_sql_handler
    }
    return validators.get(handler_type)
