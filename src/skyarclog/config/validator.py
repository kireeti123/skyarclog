"""Configuration validation utilities for SkyArcLog."""

from typing import Dict, Any, Optional, Callable, List, Union, Type
from dataclasses import dataclass
import logging
import importlib
import inspect
from pathlib import Path
import json


__all__ = [
    'ConfigValidationError',
    'ConfigValidationWarning',
    'validate_configuration',
    'validate_formatters',
    'validate_listeners'
]


@dataclass
class ValidationContext:
    """Context for validation operations."""
    path: List[str]
    warnings: List[str]
    
    def add_warning(self, message: str) -> None:
        """Add a warning message with current path context."""
        path_str = '.'.join(self.path) if self.path else 'root'
        self.warnings.append(f"{path_str}: {message}")
    
    def with_path(self, segment: str) -> 'ValidationContext':
        """Create new context with added path segment."""
        return ValidationContext(
            path=self.path + [segment],
            warnings=self.warnings
        )


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""
    def __init__(self, message: str, path: Optional[List[str]] = None):
        self.path = path or []
        path_str = '.'.join(self.path) if self.path else 'root'
        super().__init__(f"{path_str}: {message}")


class ConfigValidationWarning(Warning):
    """Warning for non-critical configuration issues."""
    pass


def validate_type(value: Any, expected_type: Union[Type, tuple], path: List[str]) -> None:
    """Validate value is of expected type.
    
    Args:
        value: Value to validate
        expected_type: Expected type or tuple of types
        path: Current config path for error reporting
    
    Raises:
        ConfigValidationError: If value is not of expected type
    """
    if not isinstance(value, expected_type):
        raise ConfigValidationError(
            f"Expected type {expected_type}, got {type(value)}",
            path
        )


def validate_required_keys(config: Dict, required: List[str], path: List[str]) -> None:
    """Validate required keys exist in config.
    
    Args:
        config: Configuration dictionary
        required: List of required keys
        path: Current config path for error reporting
    
    Raises:
        ConfigValidationError: If any required key is missing
    """
    for key in required:
        if key not in config:
            raise ConfigValidationError(f"Missing required key: {key}", path)


def validate_configuration(config: Dict[str, Any]) -> List[str]:
    """Comprehensive validation of the entire logging configuration.
    
    Args:
        config: Full configuration dictionary
    
    Returns:
        List of warning messages
    
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    context = ValidationContext(path=[], warnings=[])
    
    # Validate required top-level keys
    validate_required_keys(
        config,
        ['version', 'name', 'listeners', 'formatters', 'loggers'],
        context.path
    )
    
    # Validate version
    validate_type(config['version'], (int, float), context.path + ['version'])
    
    # Validate formatters
    if 'formatters' in config:
        validate_formatters(config['formatters'], context.with_path('formatters'))
    
    # Validate listeners
    if 'listeners' in config:
        validate_listeners(config['listeners'], context.with_path('listeners'))
    
    # Validate loggers
    if 'loggers' in config:
        validate_loggers(config['loggers'], context.with_path('loggers'))
    
    return context.warnings


def validate_loggers(loggers: Dict[str, Any], context: ValidationContext) -> None:
    """Validate logger configurations.
    
    Args:
        loggers: Logger configurations
        context: Validation context
    
    Raises:
        ConfigValidationError: If logger configuration is invalid
    """
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    for name, config in loggers.items():
        logger_context = context.with_path(name)
        
        # Validate logger config is dictionary
        validate_type(config, dict, logger_context.path)
        
        # Validate level if present
        if 'level' in config:
            level = config['level'].upper()
            if level not in valid_levels:
                raise ConfigValidationError(
                    f"Invalid level: {level}. Must be one of {valid_levels}",
                    logger_context.path
                )
        
        # Validate handlers if present
        if 'handlers' in config:
            validate_type(config['handlers'], list, logger_context.path + ['handlers'])
            
            # Check handler references exist
            for handler in config['handlers']:
                if handler not in context.handlers:
                    logger_context.add_warning(
                        f"Handler '{handler}' referenced but not defined"
                    )


def validate_formatters(formatters: Dict[str, Any], context: ValidationContext) -> None:
    """Validate formatters configuration.
    
    Args:
        formatters: Formatters configuration dictionary
        context: Validation context
    
    Raises:
        ConfigValidationError: If formatter configuration is invalid
    """
    for name, config in formatters.items():
        formatter_context = context.with_path(name)
        
        # Validate formatter config is dictionary
        validate_type(config, dict, formatter_context.path)
        
        # Get formatter type
        formatter_type = config.get('type', name)
        
        try:
            # Import formatter module
            module_name = f"skyarclog.formatters.{formatter_type}"
            module = importlib.import_module(module_name)
            
            # Find formatter class
            formatter_classes = [
                obj for _, obj in inspect.getmembers(module)
                if inspect.isclass(obj) and obj.__name__.endswith('Formatter')
            ]
            
            if not formatter_classes:
                raise ConfigValidationError(
                    f"No formatter class found in module {module_name}",
                    formatter_context.path
                )
            
            # Validate formatter config
            formatter_class = formatter_classes[0]
            validate_formatter_config(formatter_type, config)
            
        except ImportError:
            raise ConfigValidationError(
                f"Formatter type '{formatter_type}' not found",
                formatter_context.path
            )
        except Exception as e:
            raise ConfigValidationError(str(e), formatter_context.path)


def validate_listeners(listeners: Dict[str, Any], context: ValidationContext) -> None:
    """Validate listeners configuration.
    
    Args:
        listeners: Listeners configuration dictionary
        context: Validation context
    
    Raises:
        ConfigValidationError: If listener configuration is invalid
    """
    for name, config in listeners.items():
        listener_context = context.with_path(name)
        
        # Validate listener config is dictionary
        validate_type(config, dict, listener_context.path)
        
        # Skip if not enabled
        if not config.get('enabled', True):
            continue
        
        # Get listener type
        listener_type = config.get('type', name)
        
        try:
            # Import listener module
            module_name = f"skyarclog.listeners.{listener_type}"
            module = importlib.import_module(module_name)
            
            # Find listener class
            listener_classes = [
                obj for _, obj in inspect.getmembers(module)
                if inspect.isclass(obj) and obj.__name__.endswith('Listener')
            ]
            
            if not listener_classes:
                raise ConfigValidationError(
                    f"No listener class found in module {module_name}",
                    listener_context.path
                )
            
            # Validate listener config
            listener_class = listener_classes[0]
            validate_listener_config(listener_type, config)
            
        except ImportError:
            raise ConfigValidationError(
                f"Listener type '{listener_type}' not found",
                listener_context.path
            )
        except Exception as e:
            raise ConfigValidationError(str(e), listener_context.path)


# Load listener schemas from JSON file
with open(Path(__file__).parent / 'listener_schemas.json') as f:
    LISTENER_SCHEMAS = json.load(f)

# Load formatter schemas from JSON file
with open(Path(__file__).parent / 'formatter_schemas.json') as f:
    FORMATTER_SCHEMAS = json.load(f)


def get_listener_schema(listener_type: str) -> Optional[Dict[str, Any]]:
    """Get schema for listener type."""
    return LISTENER_SCHEMAS.get(listener_type)


def get_formatter_schema(formatter_type: str) -> Optional[Dict[str, Any]]:
    """Get schema for formatter type."""
    return FORMATTER_SCHEMAS.get(formatter_type)


def validate_listener_config(listener_type: str, config: Dict[str, Any]) -> None:
    """Validate listener configuration against its schema."""
    schema = get_listener_schema(listener_type)
    if not schema:
        raise ConfigValidationError(f"No schema found for listener type '{listener_type}'")
    
    # Validate required fields
    validate_required_keys(config, list(schema['required_fields'].keys()), [listener_type])
    
    # Validate types for required fields
    for field, expected_type in schema['required_fields'].items():
        validate_type(config[field], expected_type, [listener_type, field])
    
    # Validate optional fields
    for field, expected_type in schema['optional_fields'].items():
        if field in config:
            validate_type(config[field], expected_type, [listener_type, field])


def validate_formatter_config(formatter_type: str, config: Dict[str, Any]) -> None:
    """Validate formatter configuration against its schema."""
    schema = get_formatter_schema(formatter_type)
    if not schema:
        raise ConfigValidationError(f"No schema found for formatter type '{formatter_type}'")
    
    # Validate required fields
    validate_required_keys(config, list(schema['required_fields'].keys()), [formatter_type])
    
    # Validate types for required fields
    for field, expected_type in schema['required_fields'].items():
        validate_type(config[field], expected_type, [formatter_type, field])
    
    # Validate optional fields
    for field, expected_type in schema['optional_fields'].items():
        if field in config:
            validate_type(config[field], expected_type, [formatter_type, field])
