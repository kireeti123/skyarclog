"""Console listener for SkyArcLog."""

import sys
import json
from typing import Any, Dict, Optional
from colorama import init, Fore, Style
from ..base_listener import BaseListener
from ...formatters import create_formatter
from skyarclog import config
from skyarclog.config.schemas import validate_listener_config
import warnings

# Initialize colorama for cross-platform color support
init()

class ConsoleListener(BaseListener):
    """Listener that outputs log messages to the console with color support."""

    def __init__(self):
        """Initialize the console listener."""
        super().__init__()
        self._colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bold'
        }
        self._use_colors = True
        self._show_timestamp = True
        self._timestamp_format = '%Y-%m-%d %H:%M:%S.%f'
        self._show_level = True
        self._show_thread = True
        self._show_process = True
        self._output = sys.stdout

    def initialize(self, name, config):
        """Initialize the listener with configuration.
        
        Args:
            name: Name of the listener instance
            config: Configuration dictionary containing:
                - format: Output format (e.g., 'json')
                - colors.enabled: Whether to use colors
                - colors.[level]: Color for each log level
                - output: 'stdout' or 'stderr'
                - show_timestamp: Whether to show timestamps
                - timestamp_format: Format for timestamps
                - show_level: Whether to show log level
                - show_thread: Whether to show thread info
                - show_process: Whether to show process info
        """
        super().initialize(name, config)
        
        # Configure colors
        color_config = config.get('colors', {})
        self._use_colors = color_config.get('enabled', True)
        if self._use_colors:
            for level, color in color_config.items():
                if level != 'enabled' and level in self._colors:
                    self._colors[level] = color
        
        # Configure output stream
        output = config.get('output', 'stdout').lower()
        self._output = sys.stderr if output == 'stderr' else sys.stdout
        
        # Configure display options
        self._show_timestamp = config.get('show_timestamp', True)
        self._timestamp_format = config.get('timestamp_format', self._timestamp_format)
        self._show_level = config.get('show_level', True)
        self._show_thread = config.get('show_thread', True)
        self._show_process = config.get('show_process', True)

        self._configure_formatter()

    def _configure_formatter(self):
        """Configure the formatter based on configuration."""
        format_name = self._config.get('format', 'text')
        
        try:
            # Get formatter config from global formatters section
            formatter_config = self.get_formatter_config(format_name)
            formatter = create_formatter(format_name, formatter_config)
            self._formatters = [formatter]
        except Exception as e:
            warnings.warn(f"Failed to configure formatter {format_name}: {e}. Using default text formatter.")
            # Use a default text formatter as fallback
            formatter = create_formatter('text', {})
            self._formatters = [formatter]

    def get_formatter_config(self, format_name):
        """Get formatter configuration from global formatters section.
        
        Args:
            format_name: Name of the format/formatter
            
        Returns:
            Formatter configuration dictionary
        """
        # Access the global formatters configuration
        formatters_config = self._config.get('formatters', {})
        return formatters_config.get(format_name, {})

    def _get_color(self, level):
        """Get the color code for a log level.
        
        Args:
            level: Log level
            
        Returns:
            ANSI color code
        """
        if not self._use_colors:
            return ''

        color_str = self._colors.get(level, '')
        if not color_str:
            return ''

        parts = color_str.split(',')
        color = getattr(Fore, parts[0].upper(), '')
        style = Style.BRIGHT if 'bold' in parts else ''
        return color + style

    def handle(self, message):
        """Handle a log message.
        
        Args:
            message: Log message to handle
        """
        if not self.enabled:
            return

        # Apply formatters and ensure application name
        transformed_message = self._apply_formatters(message)

        # Extract log details
        timestamp = transformed_message.get('timestamp', '')
        level = transformed_message.get('level', 'INFO')
        msg = transformed_message.get('message', '')
        
        # Determine log level string and color
        level_str = f" [{level}] " if level else " "
        
        # Prepare context information
        context_str = ""
        thread = transformed_message.get('thread')
        process = transformed_message.get('process')
        
        if thread or process:
            context_parts = []
            if thread:
                context_parts.append(f"thread={thread}")
            if process:
                context_parts.append(f"process={process}")
            context_str = f" ({', '.join(context_parts)}) "

        # Prepare extra information
        extra = {k: v for k, v in transformed_message.items() 
                if k not in ('message', 'timestamp', 'level', 'thread', 'process', 'application')}

        # Construct the final message
        output = f"{timestamp}{level_str}{context_str}{msg}"
        
        # Add application name if present
        app_name = transformed_message.get('application', '')
        if app_name:
            output = f"[{app_name}] {output}"
        
        if extra:
            output = f"{output} {json.dumps(extra)}"

        # Write to console with color
        color = self._get_color(level)
        reset = Style.RESET_ALL if color else ''
        print(f"{color}{output}{reset}", file=self._output)
        self._output.flush()

    def log(self, level, message, **kwargs):
        """
        Log a message with the specified level.
        
        Args:
            level: Log level (e.g., 'DEBUG', 'INFO')
            message: Log message
            **kwargs: Additional context information
        """
        # Prepare log message dictionary
        log_message = {
            'level': level,
            'message': message,
            **kwargs
        }
        
        # Use the existing handle method
        self.handle(log_message)

    def flush(self):
        """Flush the output stream."""
        self._output.flush()

    def close(self):
        """Clean up resources."""
        self.flush()

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration for the console listener."""
        validate_listener_config('console', config)  # Use schema validation
