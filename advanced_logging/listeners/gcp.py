"""
Google Cloud Logging listener for advanced logging framework.
"""

import json
try:
    from google.cloud import logging
except ImportError:
    print("GCP listener requires google-cloud-logging package")

from .base import BaseListener

class GoogleCloudListener(BaseListener):
    """
    Listener that logs to Google Cloud Logging
    """
    def __init__(self, project_id: str = None, log_name: str = "python_logs",
                 credentials_path: str = None):
        """
        Initialize Google Cloud Logging listener
        
        :param project_id: Optional Google Cloud project ID
        :param log_name: Name for the log entries
        :param credentials_path: Optional path to service account credentials file
        """
        try:
            if credentials_path:
                self.client = logging.Client.from_service_account_json(
                    credentials_path,
                    project=project_id
                )
            else:
                self.client = logging.Client(project=project_id)
            
            self.logger = self.client.logger(log_name)
        except Exception as e:
            print(f"Google Cloud Logging initialization error: {e}")

    def emit(self, log_entry: str):
        """
        Send log entry to Google Cloud Logging
        
        :param log_entry: Formatted log entry
        """
        try:
            log_data = json.loads(log_entry)
            severity = self._map_severity(log_data.get('level', 'INFO'))
            
            self.logger.log_struct(
                log_data,
                severity=severity
            )
        except Exception as e:
            print(f"Google Cloud Logging error: {e}")

    def _map_severity(self, level: str) -> str:
        """
        Map log level to Google Cloud severity
        
        :param level: Log level from the framework
        :return: Corresponding Google Cloud severity
        """
        severity_map = {
            'DEBUG': 'DEBUG',
            'INFO': 'INFO',
            'WARNING': 'WARNING',
            'ERROR': 'ERROR',
            'CRITICAL': 'CRITICAL'
        }
        return severity_map.get(level.upper(), 'DEFAULT')
