"""Elasticsearch listener with bulk indexing and connection pooling."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from elasticsearch import Elasticsearch, helpers
from ..core import BaseListener

class ElasticsearchListener(BaseListener):
    """Elasticsearch listener with optimized bulk operations."""
    
    def __init__(self,
                 hosts: List[str] = ['http://localhost:9200'],
                 index_prefix: str = 'logs-',
                 batch_size: int = 1000,
                 flush_interval: float = 5.0,
                 max_retries: int = 3,
                 timeout: int = 30,
                 max_connections: int = 10,
                 sniff_on_start: bool = True,
                 sniff_on_connection_fail: bool = True):
        """
        Initialize Elasticsearch listener with connection pooling and batching.
        
        Args:
            hosts: List of Elasticsearch hosts
            index_prefix: Prefix for index names
            batch_size: Number of logs to batch before bulk indexing
            flush_interval: Maximum time to wait before flushing batch (seconds)
            max_retries: Maximum number of retries for failed operations
            timeout: Connection timeout in seconds
            max_connections: Maximum number of connections per node
            sniff_on_start: Whether to sniff for nodes on startup
            sniff_on_connection_fail: Whether to sniff for nodes on connection failure
        """
        super().__init__()
        
        # Initialize client with connection pooling
        self.client = Elasticsearch(
            hosts,
            retry_on_timeout=True,
            max_retries=max_retries,
            timeout=timeout,
            maxsize=max_connections,
            sniff_on_start=sniff_on_start,
            sniff_on_connection_fail=sniff_on_connection_fail
        )
        
        self.index_prefix = index_prefix
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Initialize batch processing
        self.batch: List[Dict[str, Any]] = []
        self.last_flush = datetime.now()
    
    def _get_index_name(self) -> str:
        """Get the current index name based on date."""
        return f"{self.index_prefix}{datetime.now().strftime('%Y.%m.%d')}"
    
    def _create_index_template(self):
        """Create or update the index template for optimal logging."""
        template = {
            "index_patterns": [f"{self.index_prefix}*"],
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "refresh_interval": "5s",
                "index.mapping.total_fields.limit": 2000,
                "index.mapping.ignore_malformed": True,
                "index.translog.durability": "async",
                "index.translog.sync_interval": "5s"
            },
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "logger": {"type": "keyword"},
                    "thread": {"type": "keyword"},
                    "stack_trace": {"type": "text"},
                    "additional_info": {"type": "object"}
                }
            }
        }
        
        self.client.indices.put_template(
            name=f"{self.index_prefix}template",
            body=template
        )
    
    def _should_flush(self) -> bool:
        """Check if batch should be flushed based on size or time."""
        if len(self.batch) >= self.batch_size:
            return True
        time_since_flush = (datetime.now() - self.last_flush).total_seconds()
        if time_since_flush >= self.flush_interval:
            return True
        return False
    
    def _flush_batch(self):
        """Flush the current batch using bulk indexing."""
        if not self.batch:
            return
            
        actions = []
        index_name = self._get_index_name()
        
        for log_entry in self.batch:
            action = {
                "_index": index_name,
                "_source": log_entry
            }
            actions.append(action)
        
        try:
            # Use helpers.bulk for optimized bulk indexing
            success, failed = helpers.bulk(
                self.client,
                actions,
                stats_only=True,
                raise_on_error=False
            )
            
            if failed:
                print(f"Failed to index {failed} log entries")
                
        except Exception as e:
            print(f"Error during bulk indexing: {e}")
            
        finally:
            self.batch = []
            self.last_flush = datetime.now()
    
    def handle_log(self, log_entry: Dict[str, Any]):
        """
        Handle incoming log entry with batching.
        
        Args:
            log_entry: Log entry to process
        """
        # Ensure timestamp is in correct format
        if 'timestamp' not in log_entry:
            log_entry['timestamp'] = datetime.utcnow().isoformat()
            
        self.batch.append(log_entry)
        
        if self._should_flush():
            self._flush_batch()
    
    def search_logs(self,
                    query: str,
                    start_time: Optional[str] = None,
                    end_time: Optional[str] = None,
                    size: int = 100,
                    sort_order: str = 'desc') -> List[Dict[str, Any]]:
        """
        Search logs with efficient query optimization.
        
        Args:
            query: Search query string
            start_time: Start time in ISO format
            end_time: End time in ISO format
            size: Maximum number of results
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            List of matching log entries
        """
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query}}
                    ]
                }
            },
            "sort": [{"timestamp": {"order": sort_order}}],
            "size": size
        }
        
        # Add time range if specified
        if start_time or end_time:
            range_filter = {"range": {"timestamp": {}}}
            if start_time:
                range_filter["range"]["timestamp"]["gte"] = start_time
            if end_time:
                range_filter["range"]["timestamp"]["lte"] = end_time
            search_query["query"]["bool"]["filter"] = [range_filter]
        
        try:
            # Search across all indices matching the prefix
            response = self.client.search(
                index=f"{self.index_prefix}*",
                body=search_query
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            print(f"Error during log search: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources and flush any remaining logs."""
        self._flush_batch()
        self.client.close()
