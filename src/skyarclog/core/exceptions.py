"""Custom exceptions for SkyArcLog."""

class LoggerConfigurationWarning(Warning):
    """Warning for logger configuration issues."""

class ConfigValidationError(Exception):
    """Error raised when configuration validation fails."""

class ListenerInitializationError(Exception):
    """Error raised when a listener fails to initialize."""

class FormatterInitializationError(Exception):
    """Error raised when a formatter fails to initialize."""

class PluginLoadError(Exception):
    """Error raised when a plugin fails to load."""
