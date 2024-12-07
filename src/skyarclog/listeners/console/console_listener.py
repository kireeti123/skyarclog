"""Console listener for SkyArcLog."""

import sys
import json
from typing import Any, Dict, Optional
from colorama import init, Fore, Style
from ..base_listener import BaseListener
from ...transformers import create_transformer

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

    def initialize(self, name: str, config: Dict[str, Any]) -> None:
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

        # Configure transformer based on format
        format_name = config.get('format')
        if format_name:
            # Get transformer config from global transformers section
            transformer_config = self.get_transformer_config(format_name)
            transformer = create_transformer(format_name, transformer_config)
            self._transformers = [transformer]

    def get_transformer_config(self, format_name: str) -> Dict[str, Any]:
        """Get transformer configuration from global transformers section.
        
        Args:
            format_name: Name of the format/transformer
            
        Returns:
            Dict[str, Any]: Transformer configuration
        """
        # Access the global transformers configuration
        transformers_config = self._config.get('transformers', {})
        transformer_entry = transformers_config.get(format_name, {})
        return transformer_entry.get('config', {})

    def _get_color(self, level: str) -> str:
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

    def handle(self, message: Dict[str, Any]) -> None:
        """Handle a log message.
        
        Args:
            message: Message to write to console
        """
        # Apply transformers
        transformed_message = message
        for transformer in self._transformers:
            transformed_message = transformer.transform(transformed_message)

        # Get the base message and level
        msg = str(transformed_message.get('message', ''))
        level = transformed_message.get('level', 'INFO')

        # Format timestamp if enabled
        timestamp = ''
        if self._show_timestamp:
            ts = transformed_message.get('timestamp')
            if ts:
                timestamp = f"[{ts:{self._timestamp_format}}] "

        # Format level if enabled
        level_str = ''
        if self._show_level:
            level_str = f"[{level}] "

        # Format thread/process if enabled
        context = []
        if self._show_thread and 'thread' in transformed_message:
            context.append(f"thread={transformed_message['thread']}")
        if self._show_process and 'process' in transformed_message:
            context.append(f"process={transformed_message['process']}")
        context_str = f"[{' '.join(context)}] " if context else ""

        # Format additional fields as JSON
        extra = {k: v for k, v in transformed_message.items() 
                if k not in ('message', 'timestamp', 'level', 'thread', 'process')}

        # Construct the final message
        output = f"{timestamp}{level_str}{context_str}{msg}"
        if extra:
            output = f"{output} {json.dumps(extra)}"

        # Write to console with color
        color = self._get_color(level)
        reset = Style.RESET_ALL if color else ''
        print(f"{color}{output}{reset}", file=self._output)
        self._output.flush()

    def flush(self) -> None:
        """Flush the output stream."""
        self._output.flush()

    def close(self) -> None:
        """Clean up resources."""
        self.flush()
