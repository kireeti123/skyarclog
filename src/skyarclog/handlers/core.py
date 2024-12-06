import logging
import queue
from datetime import datetime
from logging.handlers import QueueListener
from typing import Optional

from azure.storage.blob import BlobServiceClient
from opencensus.ext.azure.log_exporter import AzureLogHandler
import jsonlogger

from .memory_handler import MemoryHandlerWithInterval
from .queue_handler import BatchQueueHandler


def create_console_handler(config: dict) -> logging.Handler:
    """Create a console logging handler."""
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt=config.get('timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
    )
    handler.setFormatter(formatter)
    return handler


def create_file_handler(config: dict) -> logging.Handler:
    """Create a file logging handler."""
    handler = logging.FileHandler(
        filename=config['filename'],
        mode=config.get('mode', 'a'),
        encoding=config.get('encoding', 'utf-8')
    )
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt=config.get('timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
    )
    handler.setFormatter(formatter)
    return handler


def create_memory_handler(config: dict, handler_creator) -> Optional[logging.Handler]:
    """Create a memory handler with interval-based flushing."""
    target_handler = handler_creator(config['target'], config['target_config'])
    if target_handler:
        return MemoryHandlerWithInterval(
            capacity=config.get('capacity', 100),
            flush_level=getattr(logging, config.get('flush_level', 'ERROR')),
            target=target_handler,
            flush_interval=config.get('flush_interval', 60),
            flush_on_capacity=config.get('flush_on_capacity', True)
        )
    return None


def create_queue_handler(config: dict, handler_creator, queue_listeners: list) -> Optional[logging.Handler]:
    """Create a queue handler with batching support."""
    log_queue = queue.Queue()
    target_handler = handler_creator(config['target'], config['target_config'])
    
    if target_handler:
        listener = QueueListener(log_queue, target_handler)
        listener.start()
        queue_listeners.append(listener)
        
        return BatchQueueHandler(
            queue=log_queue,
            batch_size=config.get('batch_size', 100)
        )
    return None


def create_blob_handler(config: dict, config_manager) -> logging.Handler:
    """Create an Azure Blob storage logging handler."""
    # Get connection string from Key Vault if it's a reference
    connection_string = (
        config_manager.get_secret(config['container_connection_string'][4:-1])
        if config['container_connection_string'].startswith('${kv:')
        else config['container_connection_string']
    )
    
    container_name = (
        config_manager.get_secret(config['container_name'][4:-1])
        if config['container_name'].startswith('${kv:')
        else config['container_name']
    )

    class AzureBlobHandler(logging.Handler):
        def __init__(self, connection_string: str, container_name: str):
            super().__init__()
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_client = self.blob_service_client.get_container_client(container_name)

        def emit(self, record):
            try:
                msg = self.format(record)
                now = datetime.now()
                blob_path = f"{now.strftime('%Y/%m/%d/%H')}/log_{now.strftime('%Y%m%d_%H%M%S_%f')}.json"
                self.container_client.upload_blob(name=blob_path, data=msg.encode('utf-8'))
            except Exception:
                self.handleError(record)

    handler = AzureBlobHandler(connection_string=connection_string, container_name=container_name)
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    return handler


def create_appinsights_handler(config: dict, config_manager) -> logging.Handler:
    """Create an Azure Application Insights handler using OpenCensus."""
    # Get instrumentation key from Key Vault if it's a reference
    instrumentation_key = (
        config_manager.get_secret(config['instrumentation_key'][4:-1])
        if config['instrumentation_key'].startswith('${kv:')
        else config['instrumentation_key']
    )

    handler = AzureLogHandler(
        instrumentation_key=instrumentation_key,
        enable_local_storage=config.get('enable_local_storage', True),
        buffer_size=config.get('buffer', {}).get('max_size', 1000),
        queue_capacity=config.get('buffer', {}).get('queue_size', 5000)
    )

    # Configure sampling if enabled
    sampling_config = config.get('sampling', {})
    if sampling_config.get('enabled', False):
        handler.setSamplingRate(sampling_config.get('rate', 1.0))
        
        # Apply sampling rules if specified
        if 'rules' in sampling_config:
            for rule in sampling_config['rules']:
                if 'includes' in rule and 'rate' in rule:
                    for level in rule['includes']:
                        handler.addSamplingRule(level, rule['rate'])

    return handler


def create_sql_handler(config: dict, config_manager) -> logging.Handler:
    """Create an Azure SQL Database handler."""
    # Get connection string from Key Vault if it's a reference
    connection_string = (
        config_manager.get_secret(config['connection_string'][4:-1])
        if config['connection_string'].startswith('${kv:')
        else config['connection_string']
    )

    class AzureSQLHandler(logging.Handler):
        def __init__(self, conn_str: str, table_name: str):
            super().__init__()
            self.connection_string = conn_str
            self.table_name = table_name

        def emit(self, record):
            try:
                msg = self.format(record)
                with pyodbc.connect(self.connection_string) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            f"INSERT INTO {self.table_name} (timestamp, level, logger, message) "
                            "VALUES (?, ?, ?, ?)",
                            (datetime.now(), record.levelname, record.name, msg)
                        )
                    conn.commit()
            except Exception:
                self.handleError(record)

    handler = AzureSQLHandler(connection_string, config['table_name'])
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    return handler
