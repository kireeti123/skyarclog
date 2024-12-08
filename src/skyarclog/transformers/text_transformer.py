"""Text Transformer for SkyArcLog."""

from .base_transformer import BaseTransformer

class TextTransformer(BaseTransformer):
    """Simple text transformer for logging."""
    
    def __init__(self):
        """Initialize the text transformer."""
        super().__init__()
        self._config = {}
    
    def configure(self, config: dict = None):
        """
        Configure the transformer.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
    
    def transform(self, message, **kwargs):
        """
        Transform the log message to text.
        
        Args:
            message: The log message to transform
            **kwargs: Additional keyword arguments
        
        Returns:
            Transformed message as a string
        """
        return str(message)
