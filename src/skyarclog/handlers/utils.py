"""Utility functions and common components for handlers."""

import logging
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger


class ExtendedJsonFormatter(jsonlogger.JsonFormatter):
    """Extended JSON formatter with additional fields and customization options."""

    def __init__(self, *args, **kwargs):
        """Initialize the formatter with default fields."""
        if 'json_default' not in kwargs:
            kwargs['json_default'] = self._json_default
        super().__init__(*args, **kwargs)

    def _json_default(self, obj: Any) -> Any:
        """Handle non-serializable objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            str: String representation of the object
        """
        try:
            return str(obj)
        except Exception:
            return f"<non-serializable: {type(obj).__name__}>"


def create_formatter(
    formatter_config: Optional[Dict] = None
) -> logging.Formatter:
    """Create a formatter based on configuration.
    
    Args:
        formatter_config (Optional[Dict]): Formatter configuration. Example:
            {
                "type": "json",  # or "string"
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "json_fields": ["timestamp", "logger", "level", "message"],
                "extras": {
                    "app_name": "myapp",
                    "environment": "production"
                }
            }
            
    Returns:
        logging.Formatter: Configured formatter
    """
    if not formatter_config:
        return ExtendedJsonFormatter()

    formatter_type = formatter_config.get('type', 'json')
    if formatter_type == 'json':
        return ExtendedJsonFormatter(
            fmt=formatter_config.get('format'),
            datefmt=formatter_config.get('datefmt'),
            json_encoder=formatter_config.get('json_encoder'),
            reserved_attrs=formatter_config.get('json_fields', []),
            **formatter_config.get('extras', {})
        )
    else:
        return logging.Formatter(
            fmt=formatter_config.get('format'),
            datefmt=formatter_config.get('datefmt')
        )


def set_handler_attributes(
    handler: logging.Handler,
    config: Dict
) -> logging.Handler:
    """Set common handler attributes from configuration.
    
    Args:
        handler (logging.Handler): Handler to configure
        config (Dict): Handler configuration. Example:
            {
                "level": "INFO",
                "formatter": {
                    "type": "json",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "filters": ["filter1", "filter2"]
            }
            
    Returns:
        logging.Handler: Configured handler
    """
    # Set level
    level = config.get('level', 'INFO')
    handler.setLevel(getattr(logging, level.upper()))

    # Set formatter
    formatter_config = config.get('formatter')
    handler.setFormatter(create_formatter(formatter_config))

    # Set filters (if implemented)
    filters = config.get('filters', [])
    for filter_name in filters:
        if hasattr(logging, filter_name):
            handler.addFilter(getattr(logging, filter_name)())

    return handler
