"""File listener implementation."""

from typing import Dict, Any
import os
from datetime import datetime
from ..base_listener import BaseListener

class FileListener(BaseListener):
    """Listener that writes log messages to a file."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize file listener.
        
        Args:
            config: Listener configuration
        """
        super().__init__(config)
        self._file_path = self._config.get('file_path')
        if not self._file_path:
            raise ValueError("File path not provided")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        
        # Set up file mode (append by default)
        self._file_mode = 'a' if self._config.get('append', True) else 'w'
        self._file = None
        self._open_file()

    def _open_file(self) -> None:
        """Open the log file."""
        try:
            self._file = open(
                self._file_path,
                mode=self._file_mode,
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
        except IOError as e:
            raise RuntimeError(f"Failed to write to log file: {e}")

    def close(self) -> None:
        """Close the log file."""
        if self._file:
            self._file.close()
            self._file = None
