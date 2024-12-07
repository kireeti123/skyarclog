"""Registry for managing log listeners."""

from typing import Dict, Type, List
from .base_listener import BaseListener


class ListenerRegistry:
    """Registry for managing and creating log listeners."""

    _listeners: Dict[str, Type[BaseListener]] = {}
    _active_listeners: List[BaseListener] = []

    @classmethod
    def register(cls, name: str, listener_class: Type[BaseListener]) -> None:
        """Register a new listener type.
        
        Args:
            name: Name of the listener type
            listener_class: Listener class to register
        """
        if not issubclass(listener_class, BaseListener):
            raise ValueError(f"Listener class must inherit from BaseListener: {listener_class}")
        cls._listeners[name] = listener_class

    @classmethod
    def create_listener(cls, name: str, config: dict) -> BaseListener:
        """Create a new listener instance.
        
        Args:
            name: Name of the listener type to create
            config: Configuration for the listener
            
        Returns:
            BaseListener: Created listener instance
            
        Raises:
            KeyError: If listener type is not registered
        """
        if name not in cls._listeners:
            raise KeyError(f"Listener type not registered: {name}")
        
        listener = cls._listeners[name]()
        listener.initialize(config)
        cls._active_listeners.append(listener)
        return listener

    @classmethod
    def get_active_listeners(cls) -> List[BaseListener]:
        """Get all active listeners.
        
        Returns:
            List[BaseListener]: List of active listeners
        """
        return cls._active_listeners

    @classmethod
    def cleanup(cls) -> None:
        """Clean up all active listeners."""
        for listener in cls._active_listeners:
            try:
                listener.close()
            except Exception as e:
                # Log error but continue cleanup
                print(f"Error closing listener: {e}")
        cls._active_listeners.clear()
