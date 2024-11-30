"""
AWS CloudWatch listener for advanced logging framework.
"""

import json
try:
    import boto3
except ImportError:
    print("AWS listener requires boto3 package")

from .base import BaseListener

class CloudWatchListener(BaseListener):
    """
    Listener that logs to AWS CloudWatch
    """
    def __init__(self, log_group: str, log_stream: str, region: str = None, 
                 aws_access_key_id: str = None, aws_secret_access_key: str = None):
        """
        Initialize CloudWatch listener
        
        :param log_group: CloudWatch log group name
        :param log_stream: CloudWatch log stream name
        :param region: Optional AWS region
        :param aws_access_key_id: Optional AWS access key ID
        :param aws_secret_access_key: Optional AWS secret access key
        """
        session_kwargs = {}
        if region:
            session_kwargs['region_name'] = region
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })

        self.client = boto3.client('logs', **session_kwargs)
        self.log_group = log_group
        self.log_stream = log_stream
        self._ensure_log_group_exists()
        self._ensure_log_stream_exists()

    def _ensure_log_group_exists(self):
        """
        Create log group if it doesn't exist
        """
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            print(f"CloudWatch log group creation error: {e}")

    def _ensure_log_stream_exists(self):
        """
        Create log stream if it doesn't exist
        """
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            print(f"CloudWatch log stream creation error: {e}")

    def emit(self, log_entry: str):
        """
        Send log entry to CloudWatch
        
        :param log_entry: Formatted log entry
        """
        try:
            log_data = json.loads(log_entry)
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'timestamp': int(log_data.get('timestamp', 0) * 1000),
                    'message': json.dumps(log_data)
                }]
            )
        except Exception as e:
            print(f"CloudWatch logging error: {e}")
