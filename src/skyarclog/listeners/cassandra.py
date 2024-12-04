"""Cassandra listener with batch processing and connection pooling."""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import uuid
from cassandra.cluster import Cluster, Session, ExecutionProfile
from cassandra.policies import RoundRobinPolicy, RetryPolicy
from cassandra.query import BatchStatement, SimpleStatement
from cassandra.auth import PlainTextAuthProvider
from ..core import BaseListener

class CassandraListener(BaseListener):
    """Cassandra listener with optimized batch operations."""
    
    def __init__(self,
                 contact_points: List[str] = ['localhost'],
                 port: int = 9042,
                 keyspace: str = 'logging',
                 table_name: str = 'logs',
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 batch_size: int = 500,
                 flush_interval: float = 2.0,
                 consistency_level: str = 'LOCAL_QUORUM',
                 replication_factor: int = 3,
                 max_connections_per_host: int = 10):
        """
        Initialize Cassandra listener with connection pooling and batching.
        
        Args:
            contact_points: List of Cassandra nodes
            port: Cassandra port
            keyspace: Keyspace name
            table_name: Table name for logs
            username: Optional username for authentication
            password: Optional password for authentication
            batch_size: Number of logs to batch before writing
            flush_interval: Maximum time to wait before flushing batch (seconds)
            consistency_level: Write consistency level
            replication_factor: Replication factor for keyspace
            max_connections_per_host: Maximum connections per Cassandra node
        """
        super().__init__()
        
        # Initialize connection
        auth_provider = None
        if username and password:
            auth_provider = PlainTextAuthProvider(username=username, password=password)
        
        # Configure execution profile for performance
        profile = ExecutionProfile(
            load_balancing_policy=RoundRobinPolicy(),
            retry_policy=RetryPolicy(),
            consistency_level=consistency_level,
            request_timeout=30
        )
        
        self.cluster = Cluster(
            contact_points=contact_points,
            port=port,
            auth_provider=auth_provider,
            execution_profiles={'default': profile},
            protocol_version=4,
            connection_class=max_connections_per_host
        )
        
        self.session = self.cluster.connect()
        
        # Setup keyspace and table
        self.keyspace = keyspace
        self.table_name = table_name
        self._setup_schema(replication_factor)
        
        # Prepare statements
        self.insert_stmt = self.session.prepare(
            f"""
            INSERT INTO {self.keyspace}.{self.table_name}
            (id, timestamp, level, message, logger, thread, additional_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        )
        
        # Initialize batch processing
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = BatchStatement()
        self.batch_count = 0
        self.last_flush = datetime.now()
    
    def _setup_schema(self, replication_factor: int):
        """Setup Cassandra keyspace and table schema."""
        # Create keyspace if not exists
        self.session.execute(
            f"""
            CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
            WITH replication = {{
                'class': 'SimpleStrategy',
                'replication_factor': {replication_factor}
            }}
            """
        )
        
        # Create table if not exists
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.keyspace}.{self.table_name} (
                id uuid,
                timestamp timestamp,
                level text,
                message text,
                logger text,
                thread text,
                additional_info text,
                PRIMARY KEY ((logger, level), timestamp, id)
            ) WITH CLUSTERING ORDER BY (timestamp DESC, id ASC)
            """
        )
        
        # Create indexes for efficient querying
        self.session.execute(
            f"""
            CREATE INDEX IF NOT EXISTS ON {self.keyspace}.{self.table_name} (timestamp)
            """
        )
    
    def _should_flush(self) -> bool:
        """Check if batch should be flushed based on size or time."""
        if self.batch_count >= self.batch_size:
            return True
        time_since_flush = (datetime.now() - self.last_flush).total_seconds()
        if time_since_flush >= self.flush_interval:
            return True
        return False
    
    def _flush_batch(self):
        """Execute the current batch of log entries."""
        if self.batch_count == 0:
            return
            
        try:
            self.session.execute(self.batch)
        except Exception as e:
            print(f"Error executing batch: {e}")
        finally:
            self.batch = BatchStatement()
            self.batch_count = 0
            self.last_flush = datetime.now()
    
    def handle_log(self, log_entry: Dict[str, Any]):
        """
        Handle incoming log entry with batching.
        
        Args:
            log_entry: Log entry to process
        """
        # Generate TimeUUID for time-based ordering
        log_id = uuid.uuid4()
        
        # Extract log fields with defaults
        timestamp = datetime.fromisoformat(log_entry.get('timestamp', datetime.utcnow().isoformat()))
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        logger = log_entry.get('logger', 'root')
        thread = log_entry.get('thread', 'main')
        
        # Store additional fields as JSON
        additional_info = json.dumps({
            k: v for k, v in log_entry.items()
            if k not in ['timestamp', 'level', 'message', 'logger', 'thread']
        })
        
        # Add to batch
        self.batch.add(self.insert_stmt, (
            log_id,
            timestamp,
            level,
            message,
            logger,
            thread,
            additional_info
        ))
        self.batch_count += 1
        
        if self._should_flush():
            self._flush_batch()
    
    def search_logs(self,
                    logger: Optional[str] = None,
                    level: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search logs with efficient query optimization.
        
        Args:
            logger: Logger name filter
            level: Log level filter
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of results
            
        Returns:
            List of matching log entries
        """
        # Build query based on provided filters
        query_parts = [f"SELECT * FROM {self.keyspace}.{self.table_name}"]
        where_clauses = []
        params = {}
        
        if logger:
            where_clauses.append("logger = %(logger)s")
            params['logger'] = logger
        
        if level:
            where_clauses.append("level = %(level)s")
            params['level'] = level
        
        if start_time:
            where_clauses.append("timestamp >= %(start_time)s")
            params['start_time'] = start_time
        
        if end_time:
            where_clauses.append("timestamp <= %(end_time)s")
            params['end_time'] = end_time
        
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        query_parts.append("LIMIT %(limit)s")
        params['limit'] = limit
        
        query = " ".join(query_parts)
        
        # Execute query with pagination
        statement = SimpleStatement(query, fetch_size=limit)
        
        try:
            rows = self.session.execute(statement, params)
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                log_entry = {
                    'id': str(row.id),
                    'timestamp': row.timestamp.isoformat(),
                    'level': row.level,
                    'message': row.message,
                    'logger': row.logger,
                    'thread': row.thread
                }
                
                # Parse additional info
                if row.additional_info:
                    additional_info = json.loads(row.additional_info)
                    log_entry.update(additional_info)
                
                results.append(log_entry)
            
            return results
            
        except Exception as e:
            print(f"Error searching logs: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources and flush any remaining logs."""
        self._flush_batch()
        self.session.shutdown()
        self.cluster.shutdown()
