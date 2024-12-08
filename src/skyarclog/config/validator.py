"""Configuration validation utilities for SkyArcLog."""

from typing import Dict, Any
import logging

# Export the new validation function
__all__ = [
    'ConfigValidationError', 
    'validate_configuration', 
    'validate_formatters',
    'validate_handler_config',
    'validate_listeners'
]


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


def validate_configuration(config: Dict[str, Any]) -> None:
    """
    Comprehensive validation of the entire logging configuration.
    
    Args:
        config: Full configuration dictionary
    
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Validate required top-level keys
    required_keys = ['version', 'name']
    for key in required_keys:
        if key not in config:
            raise ConfigValidationError(f"Missing required configuration key: {key}")
    
    # Validate version
    if not isinstance(config['version'], (int, float)):
        raise ConfigValidationError("Version must be a number")
    
    # Validate formatters
    if 'formatters' in config:
        validate_formatters(config['formatters'])
    
    # Validate listeners
    if 'listeners' in config:
        validate_listeners(config['listeners'])
    
    # Optional: Additional global configuration validation
    if 'loggers' in config:
        # Validate logger configurations
        root_logger = config['loggers'].get('root', {})
        level = root_logger.get('level', 'WARNING').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            raise ConfigValidationError(
                f"Invalid root logger level: {level}. Must be one of {valid_levels}"
            )


def _validate_json_formatter(formatter: Dict[str, Any]) -> bool:
    """
    Validate JSON formatter-specific configuration.
    
    Args:
        formatter: Formatter configuration dictionary
    
    Returns:
        bool: Whether the configuration is valid
    """
    # Optional JSON-specific validations
    if 'indent' in formatter:
        indent = formatter['indent']
        if not isinstance(indent, int) or indent < 0:
            return False
    
    if 'sort_keys' in formatter:
        if not isinstance(formatter['sort_keys'], bool):
            return False
    
    return True


def validate_formatters(formatters: Dict[str, Any]) -> None:
    """
    Validate formatters configuration.
    
    Args:
        formatters (Dict): Formatters configuration dictionary
    
    Raises:
        ConfigValidationError: If any formatter configuration is invalid
    """
    # Import formatters dynamically to avoid circular imports
    from skyarclog.formatters import (
        json_formatter, 
        sql_formatter, 
        protobuf_formatter, 
        base_formatter
    )
    
    # Mapping of formatter names to their respective classes
    formatter_classes = {
        'json_formatter': json_formatter.JsonFormatter,
        'sql_formatter': sql_formatter.SqlFormatter,
        'protobuf_transformer': protobuf_formatter.ProtobufFormatter
    }
    
    # Validate each formatter
    for formatter_name, formatter_config in formatters.items():
        # Determine formatter type
        formatter_type = formatter_config.get('type', formatter_name + '_formatter')
        
        # Check if formatter type exists
        if formatter_type not in formatter_classes:
            raise ConfigValidationError(
                f"Invalid formatter type '{formatter_type}'. "
                f"Available formatters are: {list(formatter_classes.keys())}"
            )
        
        # Get the formatter class
        formatter_class = formatter_classes[formatter_type]
        
        # Validate formatter-specific configuration
        try:
            config = formatter_config.get('config', {})
            # Attempt to create an instance to validate configuration
            formatter_class(config)
        except Exception as e:
            raise ConfigValidationError(
                f"Invalid configuration for formatter '{formatter_name}': {str(e)}"
            )


def validate_listeners(listeners: Dict[str, Any]) -> None:
    """
    Validate listeners configuration.
    
    Args:
        listeners (Dict): Listeners configuration dictionary
    
    Raises:
        ConfigValidationError: If any listener configuration is invalid
    """
    # Import listeners dynamically to avoid circular imports
    from skyarclog.listeners import (
        console_listener,
        file_listener,
        azure_appinsights_listener,
        azure_blob_listener,
        azure_sql_listener,
        base_listener
    )
    
    # Mapping of listener names to their respective classes
    listener_classes = {
        'console': console_listener.ConsoleListener,
        'file': file_listener.FileListener,
        'azure-appinsights': azure_appinsights_listener.AzureAppInsightsListener,
        'azure-blob': azure_blob_listener.AzureBlobListener,
        'azure-sql': azure_sql_listener.AzureSqlListener
    }
    
    # Validate each listener
    for listener_name, listener_config in listeners.items():
        # Skip if listener is not enabled
        if not listener_config.get('enabled', False):
            continue
        
        # Determine listener type
        # Try to match based on known mappings first
        listener_type = None
        for key, cls in listener_classes.items():
            if listener_name.lower().startswith(key):
                listener_type = key
                break
        
        # If no match found, use the listener name directly
        if listener_type is None:
            listener_type = listener_name.lower()
        
        # Check if listener type exists
        if listener_type not in listener_classes:
            raise ConfigValidationError(
                f"Invalid listener type for '{listener_name}'. "
                f"Available listeners are: {list(listener_classes.keys())}"
            )
        
        # Get the listener class
        listener_class = listener_classes[listener_type]
        
        # Validate listener-specific configuration
        try:
            # Attempt to validate configuration by creating an instance
            # This will trigger any configuration validation in the listener's __init__
            listener_class(listener_config)
        except Exception as e:
            raise ConfigValidationError(
                f"Invalid configuration for listener '{listener_name}': {str(e)}"
            )
