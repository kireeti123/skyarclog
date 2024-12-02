"""
Azure Application Insights listener using OpenCensus.
"""

from typing import Any, Dict, Optional
from opencensus.ext.azure.log_exporter import AzureLogHandler
from ..formatters import BaseFormatter
from . import BaseListener
from ..security.key_vault import KeyVaultManager, KeyVaultError

class AzureAppInsightsListener(BaseListener):
    """
    Azure Application Insights listener implementation using OpenCensus.
    Supports structured logging, custom properties, and correlation.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        formatter: Optional[BaseFormatter] = None
    ):
        """
        Initialize Azure App Insights listener.
        
        Args:
            config: Listener configuration containing App Insights settings
            formatter: Optional log formatter
        """
        super().__init__(config, formatter)
        
        # Get instrumentation key from key vault
        self.instrumentation_key = self._get_instrumentation_key(config)
        
        # Initialize Azure Log Handler
        self.handler = AzureLogHandler(
            connection_string=f"InstrumentationKey={self.instrumentation_key}",
            enable_local_storage=config.get('enable_local_storage', True),
            storage_path=config.get('storage_path', None),
            storage_max_size=config.get('storage_max_size', 50 * 1024 * 1024),  # 50 MB
            storage_maintenance_period=config.get('storage_maintenance_period', 60),  # 60 seconds
            minimum_retry_interval=config.get('minimum_retry_interval', 1),  # 1 second
            maximum_retry_interval=config.get('maximum_retry_interval', 300),  # 5 minutes
            retry_count=config.get('retry_count', 3)
        )
        
        # Configure custom dimensions
        self.custom_dimensions = config.get('custom_dimensions', {})
        
    def _get_instrumentation_key(self, config: Dict[str, Any]) -> str:
        """Get App Insights instrumentation key from key vault."""
        # Get secret name for instrumentation key
        secret_name = config.get('instrumentation_key_secret')
        if not secret_name:
            raise RuntimeError("instrumentation_key_secret not provided in config")
            
        # Get key vault configuration from root config
        key_vault_config = config.get('key_vault', {})
        if not key_vault_config:
            raise RuntimeError("Key vault configuration not found in root config")
            
        try:
            vault_manager = KeyVaultManager(key_vault_config)
            return vault_manager.get_secret(secret_name)
        except KeyVaultError as e:
            raise RuntimeError(
                f"Failed to get App Insights instrumentation key from key vault: {str(e)}"
            )
            
    def emit(self, message: str, level: str, extra: Optional[Dict] = None) -> None:
        """
        Emit a log message to Azure Application Insights.
        
        Args:
            message: Log message
            level: Log level
            extra: Optional extra data
        """
        try:
            # Format the log message
            formatted = self.formatter.format(message, level, extra or {})
            
            # Prepare custom properties
            custom_properties = {
                **self.custom_dimensions,
                **(extra or {}),
                'level': level,
                'logger_name': extra.get('logger_name') if extra else None
            }
            
            # Remove None values
            custom_properties = {
                k: v for k, v in custom_properties.items() if v is not None
            }
            
            # Log to App Insights
            self.handler.emit(
                message=formatted,
                custom_dimensions=custom_properties
            )
            
        except Exception as e:
            print(f"Error writing to Azure Application Insights: {str(e)}")
            
    def flush(self) -> None:
        """Flush any buffered log messages."""
        try:
            self.handler.flush()
        except Exception as e:
            print(f"Error flushing Azure Application Insights handler: {str(e)}")
            
    def close(self) -> None:
        """Close the Azure Application Insights handler."""
        try:
            self.handler.close()
        except Exception as e:
            print(f"Error closing Azure Application Insights handler: {str(e)}")
            
    def health_check(self) -> bool:
        """
        Check if Azure Application Insights connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            # Attempt to send a test message
            self.emit(
                message="Health check",
                level="DEBUG",
                extra={'health_check': True}
            )
            return True
        except:
            return False
