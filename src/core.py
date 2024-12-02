"""
Core module for advanced logging framework with built-in security.
"""

import os
import json
import threading
from typing import Any, Dict, List, Optional
from datetime import datetime
from .formatters import BaseFormatter
from .listeners import BaseListener
from .security import LogEncryption, LogSignature, LogValidator
from async_worker import AsyncWorker

class LogManager:
    """Thread-safe singleton log manager with built-in security."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'LogManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize LogManager with security components."""
        if not hasattr(self, 'initialized'):
            self.formatters: List[BaseFormatter] = []
            self.listeners: List[BaseListener] = []
            self._setup_security()
            self.async_worker = AsyncWorker(num_workers=4, queue_size=10000)
            self.initialized = True
    
    def _setup_security(self):
        """Initialize security components."""
        # Initialize security components with secure defaults
        self.encryptor = LogEncryption(use_fernet=False)  # Use AES-GCM by default
        self.signer = LogSignature()
        self.validator = LogValidator(chain_size=100)
        
        # Store keys securely (in environment variables or secure storage in production)
        self.encryption_key = self.encryptor.export_key()
        self.private_key, self.public_key = self.signer.export_keys()
    
    @classmethod
    def get_instance(cls) -> 'LogManager':
        """Get or create singleton instance."""
        return cls()
    
    def add_formatter(self, formatter: BaseFormatter):
        """Add a log formatter."""
        self.formatters.append(formatter)
    
    def add_listener(self, listener: BaseListener):
        """Add a log listener."""
        self.listeners.append(listener)
    
    def get_listener(self, listener_type: type) -> Optional[BaseListener]:
        """Get listener by type."""
        for listener in self.listeners:
            if isinstance(listener, listener_type):
                return listener
        return None
    
    def _secure_log(self, level: str, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a secure log entry with encryption, signature, and validation."""
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "context": context or {}
        }
        
        # Sign the log entry
        signed_log = self.signer.sign_log(log_entry)
        
        # Encrypt the signed log
        encrypted_log = self.encryptor.encrypt_log(signed_log)
        
        # Add to validation chain
        self.validator.add_log(encrypted_log)
        
        return encrypted_log
    
    def _format_log(self, log_data: Dict[str, Any]) -> List[str]:
        """Format log data using all formatters."""
        formatted_logs = []
        for formatter in self.formatters:
            formatted_logs.append(formatter.format(log_data))
        return formatted_logs
    
    def _dispatch_log(self, level: str, message: str, context: Optional[Dict] = None):
        """Dispatch a secure log entry to all listeners."""
        # Create secure log entry
        secure_log = self._secure_log(level, message, context)
        
        # Format the log
        formatted_logs = self._format_log(secure_log)
        
        # Send to all listeners
        for listener in self.listeners:
            for formatted_log in formatted_logs:
                self.async_worker.enqueue(listener.emit, formatted_log)
    
    def debug(self, message: str, context: Optional[Dict] = None):
        """Log debug message."""
        self._dispatch_log("DEBUG", message, context)
    
    def info(self, message: str, context: Optional[Dict] = None):
        """Log info message."""
        self._dispatch_log("INFO", message, context)
    
    def warning(self, message: str, context: Optional[Dict] = None):
        """Log warning message."""
        self._dispatch_log("WARNING", message, context)
    
    def error(self, message: str, context: Optional[Dict] = None):
        """Log error message."""
        self._dispatch_log("ERROR", message, context)
    
    def critical(self, message: str, context: Optional[Dict] = None):
        """Log critical message."""
        self._dispatch_log("CRITICAL", message, context)
    
    def verify_log_integrity(self, block_index: int, log_index: int) -> bool:
        """Verify the integrity of a specific log entry."""
        # First verify the log in the validation chain
        if not self.validator.verify_log(block_index, log_index):
            return False
        
        # Get the log from the chain
        block = self.validator.blocks[block_index]
        encrypted_log = block["logs"][log_index]
        
        # Verify the signature
        return self.signer.verify_log(encrypted_log)
    
    def rotate_keys(self):
        """Rotate all security keys."""
        self.encryption_key = self.encryptor.rotate_key()
        self.private_key, self.public_key = self.signer.rotate_keys()
    
    def export_validation_chain(self, filepath: str):
        """Export the validation chain."""
        self.validator.export_chain(filepath)
    
    def import_validation_chain(self, filepath: str) -> bool:
        """Import and verify a validation chain."""
        return self.validator.import_chain(filepath)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            "worker_stats": self.async_worker.get_stats(),
            "num_formatters": len(self.formatters),
            "num_listeners": len(self.listeners)
        }

    def flush(self) -> None:
        """Flush all listeners."""
        for listener in self.listeners:
            try:
                listener.flush()
            except Exception as e:
                print(f"Error flushing listener: {str(e)}")

    def close(self) -> None:
        """Close all listeners and stop the async worker."""
        self.async_worker.stop()  # This will process remaining logs
        for listener in self.listeners:
            try:
                listener.close()
            except Exception as e:
                print(f"Error closing listener: {str(e)}")
