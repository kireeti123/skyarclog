"""
Database logging example using various database listeners.
"""

import os
from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import (
    SQLiteListener,
    MySQLListener,
    PostgreSQLListener,
    MongoDBListener,
    RedisListener,
    ElasticsearchListener,
    CassandraListener
)

def setup_logging():
    # Get log manager instance
    log_manager = LogManager.get_instance()
    
    # Add JSON formatter (required for database storage)
    log_manager.add_formatter(JSONFormatter())
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Add SQLite listener
    sqlite_listener = SQLiteListener(
        database="logs/app.db",
        table="logs"
    )
    log_manager.add_listener(sqlite_listener)
    
    # Add MySQL listener
    mysql_listener = MySQLListener(
        host="localhost",
        port=3306,
        database="app_logs",
        user="logger",
        password="secret"
    )
    log_manager.add_listener(mysql_listener)
    
    # Add PostgreSQL listener
    postgresql_listener = PostgreSQLListener(
        host="localhost",
        port=5432,
        database="app_logs",
        user="logger",
        password="secret"
    )
    log_manager.add_listener(postgresql_listener)
    
    # Add MongoDB listener
    mongodb_listener = MongoDBListener(
        uri="mongodb://localhost:27017",
        database="app_logs",
        collection="logs"
    )
    log_manager.add_listener(mongodb_listener)
    
    # Add Redis listener
    redis_listener = RedisListener(
        host="localhost",
        port=6379,
        password="secret",
        key_prefix="app:logs",
        max_logs=10000
    )
    log_manager.add_listener(redis_listener)
    
    # Add Elasticsearch listener
    elasticsearch_listener = ElasticsearchListener(
        hosts=["http://localhost:9200"],
        index_prefix="app-logs",
        username="elastic",
        password="secret"
    )
    log_manager.add_listener(elasticsearch_listener)
    
    # Add Cassandra listener
    cassandra_listener = CassandraListener(
        contact_points=["localhost"],
        port=9042,
        keyspace="app_logs",
        table="logs",
        username="cassandra",
        password="secret",
        replication_factor=1
    )
    log_manager.add_listener(cassandra_listener)
    
    return log_manager

def main():
    # Setup logging
    logger = setup_logging()
    
    # Log different types of events
    logger.info("User login", {
        "user_id": 123,
        "ip_address": "192.168.1.1",
        "location": "US"
    })
    
    logger.warning("High CPU usage", {
        "cpu_percent": 85,
        "memory_used": "7.5GB",
        "process_count": 120
    })
    
    logger.error("Payment failed", {
        "transaction_id": "tx_123",
        "amount": 99.99,
        "currency": "USD",
        "error_code": "INSUFFICIENT_FUNDS"
    })
    
    # Demonstrate log retrieval
    # From Redis
    redis_listener = logger.get_listener(RedisListener)
    recent_logs = redis_listener.get_logs(start=0, end=10)
    print("Recent logs from Redis:", recent_logs)
    
    # From Elasticsearch
    es_listener = logger.get_listener(ElasticsearchListener)
    error_logs = es_listener.search_logs({
        "query": {
            "match": {
                "level": "ERROR"
            }
        }
    })
    print("Error logs from Elasticsearch:", error_logs)
    
    # From Cassandra
    cassandra_listener = logger.get_listener(CassandraListener)
    warning_logs = cassandra_listener.get_logs(level="WARNING", limit=5)
    print("Warning logs from Cassandra:", warning_logs)

if __name__ == "__main__":
    main()
