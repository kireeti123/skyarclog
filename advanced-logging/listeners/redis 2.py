"""Redis listener implementation with batching and connection pooling."""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis
from redis.connection import ConnectionPool
from .base import BaseListener

class RedisListener(BaseListener):
    """Redis listener with optimized batch processing."""
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 0,
                 batch_size: int = 100,
                 flush_interval: float = 1.0,
                 key_prefix: str = 'logs:',
                 retention_days: int = 30,
                 max_pool_size: int = 10):
        """
        Initialize Redis listener with connection pooling and batching.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            batch_size: Number of logs to batch before writing
            flush_interval: Maximum time to wait before flushing batch (seconds)
            key_prefix: Prefix for Redis keys
            retention_days: Number of days to retain logs
            max_pool_size: Maximum number of connections in the pool
        """
        super().__init__()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.key_prefix = key_prefix
        self.retention_days = retention_days
        
        # Initialize connection pool
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            max_connections=max_pool_size,
            decode_responses=True
        )
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Initialize batch processing
        self.batch: List[Dict[str, Any]] = []
        self.last_flush = time.time()
    
    def _should_flush(self) -> bool:
        """Check if batch should be flushed based on size or time."""
        if len(self.batch) >= self.batch_size:
            return True
        if time.time() - self.last_flush >= self.flush_interval:
            return True
        return False
    
    def _flush_batch(self):
        """Flush the current batch of logs to Redis."""
        if not self.batch:
            return
            
        pipeline = self.redis_client.pipeline()
        
        try:
            for log_entry in self.batch:
                timestamp = log_entry.get('timestamp', datetime.utcnow().isoformat())
                key = f"{self.key_prefix}{timestamp}"
                
                # Store log entry
                pipeline.set(key, json.dumps(log_entry))
                
                # Set expiration if retention is configured
                if self.retention_days > 0:
                    pipeline.expire(key, self.retention_days * 86400)  # 86400 seconds per day
                
                # Add to time-series index
                pipeline.zadd(f"{self.key_prefix}index", {key: time.time()})
            
            # Execute all commands in single transaction
            pipeline.execute()
            
            # Clear batch and update flush time
            self.batch = []
            self.last_flush = time.time()
            
        except redis.RedisError as e:
            # Log error and retry mechanism could be implemented here
            print(f"Error flushing batch to Redis: {e}")
    
    def handle_log(self, log_entry: Dict[str, Any]):
        """
        Handle incoming log entry with batching.
        
        Args:
            log_entry: Log entry to process
        """
        self.batch.append(log_entry)
        
        if self._should_flush():
            self._flush_batch()
    
    def cleanup(self):
        """Cleanup resources and flush any remaining logs."""
        self._flush_batch()
        self.pool.disconnect()
    
    def get_logs(self, 
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None,
                 limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve logs within the specified time range.
        
        Args:
            start_time: Start timestamp (Unix timestamp)
            end_time: End timestamp (Unix timestamp)
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of log entries
        """
        index_key = f"{self.key_prefix}index"
        
        # Default to all time if not specified
        if start_time is None:
            start_time = float('-inf')
        if end_time is None:
            end_time = float('inf')
        
        # Get matching keys from time-series index
        log_keys = self.redis_client.zrangebyscore(
            index_key,
            start_time,
            end_time,
            start=0,
            num=limit
        )
        
        # Retrieve log entries in bulk
        if log_keys:
            log_entries = self.redis_client.mget(log_keys)
            return [json.loads(entry) for entry in log_entries if entry]
        
        return []
