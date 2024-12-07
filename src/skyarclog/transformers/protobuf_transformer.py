"""Protobuf transformer for converting log messages to Protocol Buffers format."""

from typing import Any, Dict, Optional
from datetime import datetime
import json
from google.protobuf import json_format
from google.protobuf.timestamp_pb2 import Timestamp
from .base_transformer import BaseTransformer


class ProtobufTransformer(BaseTransformer):
    """Transforms log messages into Protocol Buffers format."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Protobuf transformer.
        
        Args:
            config: Optional configuration with:
                - proto_module: Custom protobuf module
                - message_type: Proto message type name
                - preserve_proto_field_names: Keep proto field names
        """
        super().__init__()
        self._config = config or {}
        self._proto_module = self._config.get('proto_module')
        self._message_type = self._config.get('message_type', 'LogMessage')
        self._preserve_names = self._config.get('preserve_proto_field_names', True)

    def transform(self, message: Dict[str, Any]) -> bytes:
        """Transform log message to Protocol Buffers format.
        
        Args:
            message: Original log message
            
        Returns:
            Serialized Protocol Buffers message
        """
        # Convert datetime objects to Timestamp
        processed_message = self._process_datetime(message)
        
        if self._proto_module:
            # Use custom proto message type if provided
            proto_class = getattr(self._proto_module, self._message_type)
            proto_msg = proto_class()
            json_format.Parse(
                json.dumps(processed_message),
                proto_msg,
                ignore_unknown_fields=True
            )
        else:
            # Use default log message format
            proto_msg = self._create_default_log_message(processed_message)
            
        return proto_msg.SerializeToString()

    def _process_datetime(self, obj: Any) -> Any:
        """Convert datetime objects to Protocol Buffers Timestamp.
        
        Args:
            obj: Object to process
            
        Returns:
            Processed object with converted timestamps
        """
        if isinstance(obj, datetime):
            timestamp = Timestamp()
            timestamp.FromDatetime(obj)
            return {
                'seconds': timestamp.seconds,
                'nanos': timestamp.nanos
            }
            
        if isinstance(obj, dict):
            return {k: self._process_datetime(v) for k, v in obj.items()}
            
        if isinstance(obj, list):
            return [self._process_datetime(item) for item in obj]
            
        return obj

    def _create_default_log_message(self, message: Dict[str, Any]) -> Any:
        """Create default log message proto structure.
        
        Args:
            message: Processed message dictionary
            
        Returns:
            Protocol Buffers message
        """
        # Import here to avoid circular dependency
        from .protos.log_message_pb2 import LogMessage
        
        proto_msg = LogMessage()
        
        # Map common fields
        if 'timestamp' in message:
            proto_msg.timestamp.seconds = message['timestamp'].get('seconds', 0)
            proto_msg.timestamp.nanos = message['timestamp'].get('nanos', 0)
        
        if 'level' in message:
            proto_msg.level = message['level']
            
        if 'message' in message:
            proto_msg.message = message['message']
            
        if 'logger' in message:
            proto_msg.logger = message['logger']
            
        # Add all other fields as properties
        for key, value in message.items():
            if key not in ['timestamp', 'level', 'message', 'logger']:
                json_format.Parse(
                    json.dumps({key: value}),
                    proto_msg.properties,
                    ignore_unknown_fields=True
                )
                
        return proto_msg
