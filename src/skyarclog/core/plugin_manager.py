"""Plugin management system for dynamic loading of listeners and transformers."""

import importlib
import logging
import pkg_resources
from typing import Dict, Type, Optional, Any
from ..listeners.base_listener import BaseListener
from ..transformers.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages dynamic loading of listeners and transformers."""

    def __init__(self):
        """Initialize plugin manager."""
        self._listener_plugins: Dict[str, Type[BaseListener]] = {}
        self._transformer_plugins: Dict[str, Type[BaseTransformer]] = {}
        self._loaded_packages: Dict[str, bool] = {}

    def register_listener(self, name: str, listener_class: Type[BaseListener]) -> None:
        """Register a listener plugin.
        
        Args:
            name: Name of the listener
            listener_class: Listener class to register
        """
        self._listener_plugins[name] = listener_class

    def register_transformer(self, name: str, transformer_class: Type[BaseTransformer]) -> None:
        """Register a transformer plugin.
        
        Args:
            name: Name of the transformer
            transformer_class: Transformer class to register
        """
        self._transformer_plugins[name] = transformer_class

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

    def get_transformer(self, name: str) -> Optional[Type[BaseTransformer]]:
        """Get a transformer plugin by name.
        
        Args:
            name: Name of the transformer
            
        Returns:
            Transformer class if found, None otherwise
        """
        if name not in self._transformer_plugins:
            self._load_transformer_plugin(name)
        return self._transformer_plugins.get(name)

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

    def _load_transformer_plugin(self, name: str) -> None:
        """Load a transformer plugin by name.
        
        Args:
            name: Name of the transformer to load
        """
        try:
            # Try to load from entry points
            for entry_point in pkg_resources.iter_entry_points('skyarclog.transformers'):
                if entry_point.name == name:
                    transformer_class = entry_point.load()
                    self.register_transformer(name, transformer_class)
                    return

            # Try direct import if no entry point found
            module_name = f"skyarclog.transformers.{name}_transformer"
            try:
                module = importlib.import_module(module_name)
                class_name = f"{name.title()}Transformer"
                transformer_class = getattr(module, class_name)
                self.register_transformer(name, transformer_class)
            except (ImportError, AttributeError) as e:
                logger.debug(f"Could not load transformer plugin '{name}': {str(e)}")

        except Exception as e:
            logger.warning(f"Error loading transformer plugin '{name}': {str(e)}")

    def create_listener(self, name: str, config: Dict[str, Any]) -> Optional[BaseListener]:
        """Create a listener instance by name.
        
        Args:
            name: Name of the listener key in configuration
            config: Listener configuration
            
        Returns:
            Listener instance if successful, None otherwise
        """
        try:
            # Map listener names to their corresponding class names
            listener_type_map = {
                'console': 'console',
                'file': 'file',
                'network': 'network',
                # Add more mappings as needed
            }
            
            # Get the listener type based on the name
            type_name = listener_type_map.get(name)
            
            if not type_name:
                logger.warning(f"No listener mapping found for '{name}'")
                return None
            
            # Attempt to get the listener class
            listener_class = self.get_listener(type_name)
            
            if listener_class:
                # Create listener instance
                listener = listener_class()
                
                # Initialize the listener with its name and configuration
                listener.initialize(name, config)
                
                return listener
            
            # If no listener found, log a warning
            logger.warning(f"No listener found for type '{type_name}'")
            return None
        
        except Exception as e:
            logger.error(f"Error creating listener '{name}': {str(e)}")
            return None

    def create_transformer(self, name: str, config: Dict[str, Any]) -> Optional[BaseTransformer]:
        """Create a transformer instance by name.
        
        Args:
            name: Name of the transformer key in configuration
            config: Transformer configuration
            
        Returns:
            Transformer instance if successful, None otherwise
        """
        try:
            # Map transformer names to their corresponding class names
            transformer_type_map = {
                'json': 'json',
                'sql': 'sql',
                'protobuf': 'protobuf',
                # Add more mappings as needed
            }
            
            # Get the transformer type based on the name
            type_name = transformer_type_map.get(name)
            
            if not type_name:
                logger.warning(f"No transformer mapping found for '{name}'")
                return None
            
            # Attempt to get the transformer class
            transformer_class = self.get_transformer(type_name)
            
            if transformer_class:
                # Create transformer instance
                transformer = transformer_class()
                
                # Configure the transformer with the provided config
                transformer.configure(config)
                
                return transformer
            
            # If no transformer found, log a warning
            logger.warning(f"No transformer found for type '{type_name}'")
            return None
        
        except Exception as e:
            logger.error(f"Error creating transformer '{name}': {str(e)}")
            return None
