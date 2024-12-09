"""File listener implementation."""

from typing import Dict, Any
import os
from datetime import datetime
from ..base_listener import BaseListener
import gzip
from logging.handlers import TimedRotatingFileHandler
from ..schemas import validate_listener_config

class FileListener(BaseListener):
    """Listener that writes log messages to a file."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize file listener.
        
        Args:
            config: Listener configuration
        """
        super().__init__(config)
        self.validate_config(config)  # Validate configuration
        self._file_path = self._config.get('file_path')
        if not self._file_path:
            raise ValueError("File path not provided")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        
        # Set up file mode (append by default)
        self._file_mode = 'a' if self._config.get('append', True) else 'w'
        self._file = None
        self._open_file()

        # Handle permissions
        file_permissions = self._config.get('permissions', {}).get('file_mode', 0o644)
        dir_permissions = self._config.get('permissions', {}).get('dir_mode', 0o755)
        os.chmod(os.path.dirname(self._file_path), dir_permissions)

    def _open_file(self) -> None:
        """Open the log file."""
        try:
            self._file = TimedRotatingFileHandler(
                self._file_path,
                when=self._config.get('rotation', {}).get('when', 'midnight'),
                interval=self._config.get('rotation', {}).get('interval', 1),
                backupCount=self._config.get('rotation', {}).get('backup_count', 5),
                encoding='utf-8'
            )
        except IOError as e:
            raise RuntimeError(f"Failed to open log file: {e}")

    def emit(self, message: Dict[str, Any]) -> None:
        """Write message to file.
        
        Args:
            message: Message to write
        """
        if not self._file:
            return

        try:
            formatted_message = self.format_message(message)
            
            # Add timestamp if not present
            if 'timestamp' not in formatted_message:
                formatted_message['timestamp'] = datetime.now().isoformat()
            
            # Write message with newline
            self._file.write(str(formatted_message) + '\n')
            self._file.flush()

            # Handle compression
            if self._config.get('compression', {}).get('enabled', False):
                min_size = self._config.get('compression', {}).get('min_size', '10MB')
                if os.path.getsize(self._file_path) >= self._convert_size(min_size):
                    self._compress_file()
        except IOError as e:
            raise RuntimeError(f"Failed to write to log file: {e}")

    def _compress_file(self):
        """Compress the log file."""
        with open(self._file_path, 'rb') as f_in:
            with gzip.open(self._file_path + '.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(self._file_path)

    def _convert_size(self, size_str: str) -> int:
        """Convert size string (e.g., '10MB') to bytes."""
        size_units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        size = int(size_str[:-2])
        unit = size_str[-2:].upper()
        return size * size_units.get(unit, 1)

    def close(self) -> None:
        """Close the log file."""
        if self._file:
            self._file.close()
            self._file = None

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration for the file listener."""
        validate_listener_config('file', config)  # Use schema validation
