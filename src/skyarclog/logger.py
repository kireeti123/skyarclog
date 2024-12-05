import json
import logging
import os
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from logging.handlers import MemoryHandler, QueueHandler, QueueListener

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pythonjsonlogger import jsonlogger
import pyodbc

class MemoryHandlerWithInterval(MemoryHandler):
    """Extended MemoryHandler with time-based flushing."""
    def __init__(self, capacity: int, flush_level: int, target: logging.Handler,
                 flush_interval: int = 60, flush_on_capacity: bool = True):
        super().__init__(capacity, flushLevel=flush_level, target=target)
        self.flush_interval = flush_interval
        self.flush_on_capacity = flush_on_capacity
        self.last_flush = time.time()
        self._start_flush_timer()

    def _start_flush_timer(self):
        def flush_timer():
            while True:
                time.sleep(1)
                if time.time() - self.last_flush >= self.flush_interval:
                    self.flush()
                    self.last_flush = time.time()

        thread = threading.Thread(target=flush_timer, daemon=True)
        thread.start()

    def shouldFlush(self, record: logging.LogRecord) -> bool:
        """Determine if the handler should flush its buffer."""
        if record.levelno >= self.flushLevel:
            return True
        if self.flush_on_capacity and len(self.buffer) >= self.capacity:
            return True
        return False

class BatchQueueHandler(QueueHandler):
    """Queue handler that supports batching of records."""
    def __init__(self, queue: queue.Queue, batch_size: int = 100):
        super().__init__(queue)
        self.batch_size = batch_size
        self.batch = []
        self.batch_lock = threading.Lock()

    def enqueue(self, record: logging.LogRecord) -> None:
        """Batch records before enqueueing them."""
        with self.batch_lock:
            self.batch.append(record)
            if len(self.batch) >= self.batch_size:
                self.queue.put(self.batch)
                self.batch = []

    def flush(self) -> None:
        """Flush any remaining records in the batch."""
        with self.batch_lock:
            if self.batch:
                self.queue.put(self.batch)
                self.batch = []

class SkyArcLogger:
    def __init__(self, config_path: str = None):
        """Initialize the SkyArc Logger with configuration."""
        self.config = self._load_config(config_path)
        self.loggers: Dict[str, logging.Logger] = {}
        self.queue_listeners: List[QueueListener] = []
        self._setup_logging()

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load configuration from the specified JSON file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), 'skyarclog_logging.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config

    def _setup_logging(self):
        """Set up all configured logging handlers."""
        listeners = self.config.get('listeners', {})
        
        for logger_name, logger_config in self.config.get('loggers', {}).items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, logger_config.get('level', 'INFO')))
            
            for handler_name in logger_config.get('handlers', []):
                if handler_name in listeners and listeners[handler_name].get('enabled', False):
                    handler = self._create_handler(handler_name, listeners[handler_name])
                    if handler:
                        logger.addHandler(handler)
            
            self.loggers[logger_name] = logger

    def _create_handler(self, handler_name: str, config: dict) -> Optional[logging.Handler]:
        """Create a logging handler based on the configuration."""
        handlers = {
            'console': self._create_console_handler,
            'file': self._create_file_handler,
            'azure-blob': self._create_blob_handler,
            'azure-appinsights': self._create_appinsights_handler,
            'azure-sql': self._create_sql_handler,
            'memory': self._create_memory_handler,
            'queue': self._create_queue_handler
        }
        
        handler_creator = handlers.get(handler_name)
        if handler_creator:
            return handler_creator(config)
        return None

    def _create_console_handler(self, config: dict) -> logging.Handler:
        """Create a console logging handler."""
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
            datefmt=config.get('timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
        )
        handler.setFormatter(formatter)
        return handler

    def _create_blob_handler(self, config: dict) -> logging.Handler:
        """Create an Azure Blob storage logging handler."""
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

        handler = AzureBlobHandler(
            connection_string=os.getenv(config['container_connection_string'].strip('${}')),
            container_name=os.getenv(config['container_name'].strip('${}'))
        )
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        return handler

    def _create_appinsights_handler(self, config: dict) -> logging.Handler:
        """Create an Azure Application Insights logging handler."""
        tracer_provider = TracerProvider()
        azure_exporter = AzureMonitorTraceExporter(
            connection_string=os.getenv(config['connection_string'].strip('${}'))
        )
        span_processor = BatchSpanProcessor(azure_exporter)
        tracer_provider.add_span_processor(span_processor)

        class AppInsightsHandler(logging.Handler):
            def __init__(self, exporter):
                super().__init__()
                self.exporter = exporter

            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.exporter.export([{
                        'name': record.name,
                        'message': msg,
                        'severity': record.levelname,
                        'time': datetime.utcnow().isoformat()
                    }])
                except Exception:
                    self.handleError(record)

        handler = AppInsightsHandler(azure_exporter)
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        return handler

    def _create_sql_handler(self, config: dict) -> logging.Handler:
        """Create an Azure SQL Database logging handler."""
        class AzureSQLHandler(logging.Handler):
            def __init__(self, connection_string: str):
                super().__init__()
                self.conn_str = connection_string
                self._ensure_table()

            def _ensure_table(self):
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ApplicationLogs')
                        CREATE TABLE ApplicationLogs (
                            Id BIGINT IDENTITY(1,1) PRIMARY KEY,
                            Timestamp DATETIME2,
                            Level VARCHAR(50),
                            Logger VARCHAR(255),
                            Message NVARCHAR(MAX),
                            Exception NVARCHAR(MAX),
                            AdditionalData NVARCHAR(MAX)
                        )
                    """)
                    conn.commit()

            def emit(self, record):
                try:
                    with pyodbc.connect(self.conn_str) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO ApplicationLogs 
                            (Timestamp, Level, Logger, Message, Exception, AdditionalData)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            datetime.now(),
                            record.levelname,
                            record.name,
                            record.getMessage(),
                            getattr(record, 'exc_text', None),
                            json.dumps(getattr(record, 'extra', {}))
                        ))
                        conn.commit()
                except Exception:
                    self.handleError(record)

        handler = AzureSQLHandler(config['connection_string'])
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        return handler

    def _create_memory_handler(self, config: dict) -> logging.Handler:
        """Create a memory handler with specified targets."""
        if not config.get('enabled', False):
            return None

        target_handlers = []
        for target_name in config.get('target_handlers', []):
            target_config = self.config['listeners'].get(target_name)
            if target_config and target_config.get('enabled', False):
                handler = self._create_handler(target_name, target_config)
                if handler:
                    target_handlers.append(handler)

        if not target_handlers:
            return None

        # Create a composite handler if there are multiple targets
        target = (
            target_handlers[0] if len(target_handlers) == 1
            else logging.handlers.MemoryHandlerCollection(target_handlers)
        )

        return MemoryHandlerWithInterval(
            capacity=config.get('capacity', 1000),
            flush_level=getattr(logging, config.get('flush_level', 'ERROR')),
            target=target,
            flush_interval=config.get('flush_interval', 60),
            flush_on_capacity=config.get('flush_on_capacity', True)
        )

    def _create_queue_handler(self, config: dict) -> logging.Handler:
        """Create a queue handler with worker threads."""
        if not config.get('enabled', False):
            return None

        log_queue = queue.Queue(maxsize=config.get('queue_size', 1000))
        target_handlers = []

        for target_name in config.get('target_handlers', []):
            target_config = self.config['listeners'].get(target_name)
            if target_config and target_config.get('enabled', False):
                handler = self._create_handler(target_name, target_config)
                if handler:
                    target_handlers.append(handler)

        if not target_handlers:
            return None

        # Create queue listener with all target handlers
        listener = QueueListener(
            log_queue,
            *target_handlers,
            respect_handler_level=True
        )
        listener.start()
        self.queue_listeners.append(listener)

        # Create batch queue handler
        return BatchQueueHandler(
            queue=log_queue,
            batch_size=config.get('batch_size', 100)
        )

    def get_logger(self, name: str = 'root') -> logging.Logger:
        """Get a configured logger by name."""
        return self.loggers.get(name, self.loggers.get('root', logging.getLogger(name)))

    def __call__(self, name: str = 'root') -> logging.Logger:
        """Convenient way to get a logger instance."""
        return self.get_logger(name)

    def __del__(self):
        """Cleanup queue listeners on deletion."""
        for listener in self.queue_listeners:
            try:
                listener.stop()
            except:
                pass
