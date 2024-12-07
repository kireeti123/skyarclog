"""Factory for creating listener instances."""

import importlib
import inspect
from typing import Dict, Any, Type
from .base_listener import BaseListener
from .listener_registry import ListenerRegistry
from .azure.azure_appinsights_listener import AzureAppInsightsListener
from .azure.azure_blob_listener import AzureBlobListener
from .azure.azure_sql_listener import AzureSqlListener


class ListenerFactory:
    """Factory for creating and managing listeners."""

    _listener_packages = [
        'skyarclog.listeners.file_listener',
        # Add more listener packages here
    ]

    @classmethod
    def discover_listeners(cls) -> None:
        """Automatically discover and register all available listeners."""
        for package_name in cls._listener_packages:
            try:
                module = importlib.import_module(package_name)
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseListener) and 
                        obj != BaseListener):
                        # Convert CamelCase to snake_case for listener type
                        listener_type = cls._camel_to_snake(name)
                        if listener_type.endswith('_listener'):
                            listener_type = listener_type[:-9]  # Remove '_listener' suffix
                        ListenerRegistry.register(listener_type, obj)
            except ImportError as e:
                print(f"Warning: Could not load listener package {package_name}: {e}")

    @classmethod
    def create_listener(cls, listener_type: str, config: Dict[str, Any]) -> BaseListener:
        """Create a new listener instance based on type and configuration.
        
        Args:
            listener_type: Type of listener to create
            config: Configuration for the listener
            
        Returns:
            BaseListener: Created listener instance
            
        Raises:
            KeyError: If listener type is not registered
        """
        # Ensure listeners are discovered
        if not ListenerRegistry._listeners:
            cls.discover_listeners()

        # Add Azure listeners
        azure_listeners = {
            'azure-appinsights': AzureAppInsightsListener,
            'azure-blob': AzureBlobListener,
            'ms-sql': AzureSqlListener  # Keeping the name ms-sql for backward compatibility
        }
        if listener_type in azure_listeners:
            return azure_listeners[listener_type](**config)

        return ListenerRegistry.create_listener(listener_type, config)

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert CamelCase to snake_case.
        
        Args:
            name: CamelCase string
            
        Returns:
            str: snake_case string
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
