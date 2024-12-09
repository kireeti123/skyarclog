"""Plugin management system for dynamic loading of listeners and formatters."""

import importlib
import logging
import pkg_resources
from typing import Dict, Type, Optional, Any
from ..listeners.base_listener import BaseListener
from ..formatters.base_formatter import BaseFormatter

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages dynamic loading of listeners and formatters."""

    def __init__(self):
        """Initialize plugin manager."""
        self._listener_plugins: Dict[str, Type[BaseListener]] = {}
        self._formatter_plugins: Dict[str, Type[BaseFormatter]] = {}
        self._loaded_packages: Dict[str, bool] = {}

    def register_listener(self, name: str, listener_class: Type[BaseListener]) -> None:
        """Register a listener plugin.
        
        Args:
            name: Name of the listener
            listener_class: Listener class to register
        """
        self._listener_plugins[name] = listener_class

    def register_formatter(self, name: str, formatter_class: Type[BaseFormatter]) -> None:
        """Register a formatter plugin.
        
        Args:
            name: Name of the formatter
            formatter_class: Transformer class to register
        """
        self._formatter_plugins[name] = formatter_class

    def get_listener(self, name: str) -> Optional[Type[BaseListener]]:
        """Get a listener plugin by name.
        
        Args:
            name: Name of the listener
            
        Returns:
            Listener class if found, None otherwise
        """
        if name not in self._listener_plugins:
            self._load_listener_plugin(name)
        return self._listener_plugins.get(name)

    def get_formatter(self, name: str) -> Optional[Type[BaseFormatter]]:
        """Get a formatter plugin by name.
        
        Args:
            name: Name of the formatter
            
        Returns:
            Transformer class if found, None otherwise
        """
        if name not in self._formatter_plugins:
            self._load_formatter_plugin(name)
        return self._formatter_plugins.get(name)

    def _load_listener_plugin(self, name: str) -> None:
        """Load a listener plugin by name.
        
        Args:
            name: Name of the listener to load
        """
        try:
            # Try to load from entry points
            for entry_point in pkg_resources.iter_entry_points('skyarclog.listeners'):
                if entry_point.name == name:
                    listener_class = entry_point.load()
                    self.register_listener(name, listener_class)
                    return

            # Try direct import if no entry point found
            module_name = f"skyarclog.listeners.{name}.{name}_listener"
            try:
                module = importlib.import_module(module_name)
                class_name = f"{name.title()}Listener"
                listener_class = getattr(module, class_name)
                self.register_listener(name, listener_class)
            except (ImportError, AttributeError) as e:
                logger.debug(f"Could not load listener plugin '{name}': {str(e)}")

        except Exception as e:
            logger.warning(f"Error loading listener plugin '{name}': {str(e)}")

    def _load_formatter_plugin(self, name: str) -> None:
        """Load a formatter plugin by name.
        
        Args:
            name: Name of the formatter to load
        """
        try:
            # Try to load from entry points
            for entry_point in pkg_resources.iter_entry_points('skyarclog.formatters'):
                if entry_point.name == name:
                    formatter_class = entry_point.load()
                    self.register_formatter(name, formatter_class)
                    return

            # Try direct import if no entry point found
            module_name = f"skyarclog.formatters.{name}_formatter"
            try:
                module = importlib.import_module(module_name)
                class_name = f"{name.title()}Transformer"
                formatter_class = getattr(module, class_name)
                self.register_formatter(name, formatter_class)
            except (ImportError, AttributeError) as e:
                logger.debug(f"Could not load formatter plugin '{name}': {str(e)}")

        except Exception as e:
            logger.warning(f"Error loading formatter plugin '{name}': {str(e)}")

    def create_listener(self, name: str, config: dict) -> BaseListener:
        """Create a listener instance.
        
        Args:
            name: Name of the listener to create
            config: Configuration for the listener
            
        Returns:
            Configured listener instance
            
        Raises:
            ImportError: If listener module cannot be imported
            AttributeError: If listener class cannot be found
        """
        from ..listeners import create_listener
        return create_listener(name, config)

    def create_formatter(self, name: str, config: Dict[str, Any]) -> Optional[BaseFormatter]:
        """Create a formatter instance by name.
        
        Args:
            name: Name of the formatter key in configuration
            config: Transformer configuration
            
        Returns:
            Transformer instance if successful, None otherwise
        """
        try:
            # Map formatter names to their corresponding class names
            formatter_type_map = {
                'json': 'json',
                'sql': 'sql',
                'protobuf': 'protobuf',
                # Add more mappings as needed
            }
            
            # Get the formatter type based on the name
            type_name = formatter_type_map.get(name)
            
            if not type_name:
                logger.warning(f"No formatter mapping found for '{name}'")
                return None
            
            # Attempt to get the formatter class
            formatter_class = self.get_formatter(type_name)
            
            if formatter_class:
                # Create formatter instance
                formatter = formatter_class()
                
                # Configure the formatter with the provided config
                formatter.configure(config)
                
                return formatter
            
            # If no formatter found, log a warning
            logger.warning(f"No formatter found for type '{type_name}'")
            return None
        
        except Exception as e:
            logger.error(f"Error creating formatter '{name}': {str(e)}")
            return None
