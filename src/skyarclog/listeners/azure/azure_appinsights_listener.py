"""Azure Application Insights listener implementation."""

from typing import Any, Dict, List
from opencensus.ext.azure.log_exporter import AzureLogHandler
from ..buffered_listener import BufferedListener


class AzureAppInsightsListener(BufferedListener):
    """Listener for Azure Application Insights."""

    def __init__(self):
        """Initialize the Azure App Insights listener."""
        super().__init__()
        self._handler = None
        self._instrumentation_key = None
        self._enable_local_storage = False

    def initialize(self, name: str, config: Dict[str, Any]) -> None:
        """Initialize the listener with configuration.
        
        Args:
            name: Name of the listener instance
            config: Configuration dictionary containing:
                - instrumentation_key: Azure App Insights instrumentation key
                - enable_local_storage: Whether to enable local storage
                - buffer: Buffer configuration (inherited from BufferedListener)
        """
        super().initialize(name, config)
        
        self._instrumentation_key = config['instrumentation_key']
        self._enable_local_storage = config.get('enable_local_storage', False)
        
        self._handler = AzureLogHandler(
            connection_string=f"InstrumentationKey={self._instrumentation_key}",
            enable_local_storage=self._enable_local_storage
        )

    def _handle_transformed_message(self, message: Dict[str, Any]) -> None:
        """Handle a transformed message.
        
        Args:
            message: Message to send to App Insights
        """
        # Convert to App Insights format
        custom_dimensions = message.copy()
        level = custom_dimensions.pop('level', 'INFO')
        msg = custom_dimensions.pop('message', '')
        
        self._handler.emit({
            'msg': msg,
            'level': level,
            'custom_dimensions': custom_dimensions
        })

    def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Send a batch of messages to App Insights.
        
        Args:
            batch: List of messages to send
        """
        for message in batch:
            self._handle_transformed_message(message)
        self._handler.flush()

    def close(self) -> None:
        """Clean up resources."""
        super().close()
        if self._handler:
            self._handler.flush()
            self._handler.close()