class KeyVaultConfig:
    """Configuration manager for Azure Key Vault integration."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager

    def get_secret_or_value(self, value: str) -> str:
        """Get a secret from the config manager if it's a key vault reference, otherwise return the value.
        
        Args:
            value (str): The value to check. If it starts with '${kv:', it's treated as a key vault reference.
            
        Returns:
            str: The resolved secret value if it's a key vault reference, otherwise the original value.
        """
        if value.startswith('${kv:'):
            return self.config_manager.get_secret(value[4:-1])
        return value
