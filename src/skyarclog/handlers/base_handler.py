"""Base handler for creating and managing logging handlers."""

import logging
from typing import Optional, Dict, Callable, List

from skyarclog.config.keyvault_config import KeyVaultConfig
from skyarclog.handlers.core import (
    create_blob_handler,
    create_appinsights_handler,
    create_sql_handler,
    create_console_handler,
    create_file_handler,
    create_memory_handler,
    create_queue_handler
)
from skyarclog.handlers.utils import set_handler_attributes


class BaseHandler:
    """Base handler class for managing logging handlers."""

    def __init__(self, config_manager=None):
        """Initialize the base handler.
        
        Args:
            config_manager: Configuration manager instance for accessing secrets
        """
        self.config_manager = config_manager
        self.keyvault_config = KeyVaultConfig(config_manager)
        self._handler_creators = self._get_handler_creators()
        self.queue_listeners = []

    def _get_handler_creators(self) -> Dict[str, Callable]:
        """Get the mapping of handler names to their creation functions.
        
        Returns:
            Dict[str, Callable]: Dictionary mapping handler names to their creation functions
        """
        return {
            'console': self._create_console_handler,
            'file': self._create_file_handler,
            'memory': self._create_memory_handler,
            'queue': self._create_queue_handler,
            'azure-blob': self._create_azure_blob_handler,
            'azure-appinsights': self._create_azure_appinsights_handler,
            'azure-sql': self._create_azure_sql_handler
        }

    def create_handler(self, handler_type: str, config: dict) -> Optional[logging.Handler]:
        """Create a handler based on the configuration.
        
        Args:
            handler_type (str): Type of handler to create
            config (dict): Handler configuration
            
        Returns:
            Optional[logging.Handler]: Created handler or None if handler type not found
        """
        handler_creator = self._handler_creators.get(handler_type)
        if handler_creator:
            handler = handler_creator(config)
            if handler:
                return set_handler_attributes(handler, config)
        return None

    def _create_console_handler(self, config: dict) -> logging.Handler:
        """Create a console handler."""
        return create_console_handler(
            stream=config.get('stream'),
            level=config.get('level', 'INFO')
        )

    def _create_file_handler(self, config: dict) -> logging.Handler:
        """Create a file handler."""
        return create_file_handler(
            filename=config['filename'],
            mode=config.get('mode', 'a'),
            encoding=config.get('encoding', 'utf-8'),
            rotation_config=config.get('rotation')
        )

    def _create_memory_handler(self, config: dict) -> logging.Handler:
        """Create a memory handler."""
        return create_memory_handler(
            capacity=config.get('capacity', 1000),
            flush_interval=config.get('flush_interval', 10.0),
            target_handler_config=config.get('target_handler'),
            target_handler_creator=self.create_handler
        )

    def _create_queue_handler(self, config: dict) -> logging.Handler:
        """Create a queue handler."""
        handler, listener = create_queue_handler(
            batch_size=config.get('batch_size', 100),
            target_handlers_config=config.get('target_handlers', []),
            target_handler_creator=self.create_handler
        )
        self.queue_listeners.append(listener)
        return handler

    def _create_azure_blob_handler(self, config: dict) -> logging.Handler:
        """Create an Azure Blob storage handler."""
        connection_string = self.keyvault_config.get_secret_or_value(config['container_connection_string'])
        container_name = self.keyvault_config.get_secret_or_value(config['container_name'])
        return create_blob_handler(connection_string, container_name)

    def _create_azure_appinsights_handler(self, config: dict) -> logging.Handler:
        """Create an Azure Application Insights handler."""
        instrumentation_key = self.keyvault_config.get_secret_or_value(config['instrumentation_key'])
        return create_appinsights_handler(
            instrumentation_key=instrumentation_key,
            enable_local_storage=config.get('enable_local_storage', True),
            buffer_size=config.get('buffer', {}).get('max_size', 1000),
            queue_capacity=config.get('buffer', {}).get('queue_size', 5000),
            sampling_config=config.get('sampling')
        )

    def _create_azure_sql_handler(self, config: dict) -> logging.Handler:
        """Create an Azure SQL Database handler."""
        connection_string = self.keyvault_config.get_secret_or_value(config['connection_string'])
        return create_sql_handler(connection_string, config['table_name'])

    def stop_queue_listeners(self) -> None:
        """Stop all queue listeners."""
        for listener in self.queue_listeners:
            listener.stop()
        self.queue_listeners = []
