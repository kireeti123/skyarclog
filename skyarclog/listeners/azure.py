"""
Azure Application Insights listener for advanced logging framework.
"""

import json
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
except ImportError:
    print("Azure listener requires azure-monitor-opentelemetry and opentelemetry packages")

from .base import BaseListener

class AzureAppInsightsListener(BaseListener):
    """
    Listener that logs to Azure Application Insights
    """
    def __init__(self, connection_string: str = None):
        """
        Initialize Azure App Insights listener
        
        :param connection_string: Optional Azure Monitor connection string
        """
        try:
            if connection_string:
                configure_azure_monitor(connection_string=connection_string)
            else:
                configure_azure_monitor()
        except Exception as e:
            print(f"Azure App Insights configuration error: {e}")

    def emit(self, log_entry: str):
        """
        Log entry to Azure Application Insights
        
        :param log_entry: Formatted log entry
        """
        try:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("log_entry") as span:
                log_data = json.loads(log_entry)
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("log.level", log_data.get('level', ''))
                span.set_attribute("log.message", log_data.get('message', ''))
                
                # Add extra attributes
                extra = log_data.get('extra', {})
                for key, value in extra.items():
                    span.set_attribute(f"extra.{key}", str(value))
        except Exception as e:
            print(f"Azure App Insights logging error: {e}")
