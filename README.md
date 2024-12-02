# SkyArcLog - Advanced Logging Framework

A comprehensive, secure, and high-performance logging framework with centralized configuration, key vault integration, and support for multiple database platforms.

## Features

### 1. Key Vault Integration
- Support for multiple cloud providers:
  - Azure Key Vault
  - AWS Secrets Manager
  - Google Cloud Secret Manager
- Secure connection string management
- Environment variable substitution
- Flexible configuration

### 2. Database Support
- MSSQL
- PostgreSQL
- MongoDB
- Cassandra
- Elasticsearch
- Redis

### 3. Performance Features
- Two-tier caching system:
  - In-memory LRU cache
  - SQLite-based disk cache
- Automatic resource management
- Performance monitoring
- Dynamic scaling
- Throttling capabilities

### 4. Monitoring & Analytics
- Real-time metrics collection
- Resource usage tracking
- Performance reporting
- Health checks
- Cache statistics

### 5. Security
- Key vault-based secret management
- Encrypted connections
- Secure credential handling
- Access control integration

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Basic Setup

Create a `logging_config.json` file:

```json
{
    "version": 1.0,
    "key_vault": {
        "provider": "azure",
        "vault_url": "${AZURE_KEY_VAULT_URL}"
    },
    "listeners": {
        "mssql": {
            "enabled": true,
            "connection_string_secret": "mssql-connection-string"
        }
    }
}
```

### Full Configuration Reference

```json
{
    "version": 1.0,
    "key_vault": {
        "provider": "azure",
        "vault_url": "${AZURE_KEY_VAULT_URL}"
    },
    "listeners": {
        "mssql": {
            "enabled": true,
            "connection_string_secret": "mssql-connection-string"
        },
        "postgresql": {
            "enabled": true,
            "connection_string_secret": "postgresql-connection-string"
        },
        "mongodb": {
            "enabled": true,
            "connection_string_secret": "mongodb-connection-string"
        },
        "azure_app_insights": {
            "enabled": true,
            "instrumentation_key_secret": "appinsights-instrumentation-key",
            "enable_local_storage": true,
            "storage_path": "/tmp/appinsights",
            "custom_dimensions": {
                "environment": "${ENVIRONMENT}",
                "service": "${SERVICE_NAME}"
            }
        }
    },
    "performance": {
        "metrics_window_size": 1000,
        "max_memory_mb": 1024,
        "max_cpu_percent": 80,
        "max_disk_write_mbs": 50,
        "max_network_mbs": 50,
        "min_workers": 2,
        "max_workers": 8,
        "scale_up_threshold": 0.75,
        "scale_down_threshold": 0.25
    },
    "cache": {
        "memory": {
            "enabled": true,
            "max_size_mb": 100,
            "max_items": 10000,
            "ttl_seconds": 300
        },
        "disk": {
            "enabled": true,
            "cache_dir": "${LOG_CACHE_DIR}",
            "max_size_mb": 1024,
            "ttl_seconds": 86400
        }
    },
    "security": {
        "encryption": {
            "enabled": true,
            "key_rotation_days": 30
        }
    }
}
```

### Configuration Sections

1. **Key Vault** (`key_vault`):
   - `provider`: Cloud provider (azure, aws, google)
   - `vault_url`: Key vault URL

2. **Listeners** (`listeners`):
   - Database-specific configurations
   - Connection string secrets
   - Custom settings per listener

3. **Performance** (`performance`):
   - `metrics_window_size`: Size of metrics collection window
   - `max_memory_mb`: Maximum memory usage
   - `max_cpu_percent`: Maximum CPU usage
   - `max_disk_write_mbs`: Maximum disk write speed
   - `max_network_mbs`: Maximum network usage
   - Worker pool configuration

4. **Cache** (`cache`):
   - Memory cache settings
   - Disk cache configuration
   - TTL and size limits

5. **Security** (`security`):
   - Encryption settings
   - Key rotation policies

## Usage

### Basic Logging

```python
from advanced_logging import Logger

logger = Logger()

# Simple logging
logger.info("User logged in", extra={
    'user_id': '123',
    'action': 'login'
})

# Structured logging
logger.log({
    'level': 'INFO',
    'message': 'Payment processed',
    'transaction_id': 'tx_123',
    'amount': 100.50,
    'currency': 'USD'
})
```

### Performance Monitoring

```python
from advanced_logging.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

# Get performance report
report = monitor.get_performance_report()
print(report['metrics']['throughput'])
print(report['recommendations'])

# Check if throttling needed
if monitor.should_throttle():
    print("System under heavy load")
```

### Cache Management

```python
from advanced_logging.cache import TieredCache

cache = TieredCache()

# Cache operations
cache.put('key', value)
cached_value = cache.get('key')

# Get cache stats
stats = cache.get_stats()
print(f"Memory cache hits: {stats['memory'].hits}")
print(f"Disk cache size: {stats['disk'].size_bytes}")
```

## Environment Variables

Required environment variables:
- `AZURE_KEY_VAULT_URL`: Azure Key Vault URL
- `LOG_CACHE_DIR`: Directory for disk cache
- `ENVIRONMENT`: Environment name
- `SERVICE_NAME`: Service identifier

Optional environment variables:
- Cloud provider credentials
- Custom configuration overrides

## Best Practices

1. **Configuration**:
   - Use environment variables for sensitive values
   - Regularly rotate secrets
   - Monitor resource usage thresholds

2. **Performance**:
   - Enable caching for frequently accessed data
   - Monitor performance metrics
   - Adjust worker counts based on load

3. **Security**:
   - Use key vault for all secrets
   - Enable encryption
   - Implement access controls

4. **Maintenance**:
   - Regular cache cleanup
   - Monitor disk usage
   - Review performance reports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
