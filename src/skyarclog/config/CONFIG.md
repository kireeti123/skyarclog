# Logging Configuration Guide

This document provides a comprehensive guide to configuring the SkyArcLog framework using `logging_config.json`.

## Configuration Structure

```json
{
    "version": "1.0",
    "key_vault": { ... },
    "listeners": { ... },
    "performance": { ... },
    "cache": { ... },
    "security": { ... }
}
```

## Required vs Optional Fields

### Root Level
| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `version` | ✅ | string | Configuration version (e.g., "1.0") |
| `key_vault` | ✅ | object | Key vault configuration |
| `listeners` | ✅ | object | Logging listeners configuration |
| `performance` | ❌ | object | Performance monitoring settings |
| `cache` | ❌ | object | Caching configuration |
| `security` | ❌ | object | Security settings |

### Key Vault Configuration
```json
{
    "key_vault": {
        "provider": "azure",
        "vault_url": "${AZURE_KEY_VAULT_URL}"
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `provider` | ✅ | string | Cloud provider ("azure", "aws", "google") |
| `vault_url` | ✅ | string | Key vault URL or endpoint |

### Listeners Configuration

#### MSSQL Listener
```json
{
    "mssql": {
        "enabled": true,
        "connection_string_secret": "mssql-connection-string"
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `enabled` | ✅ | boolean | Enable/disable the listener |
| `connection_string_secret` | ✅ | string | Secret name for connection string |

#### Azure App Insights Listener
```json
{
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
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `enabled` | ✅ | boolean | Enable/disable the listener |
| `instrumentation_key_secret` | ✅ | string | Secret name for instrumentation key |
| `enable_local_storage` | ❌ | boolean | Enable local storage (default: true) |
| `storage_path` | ❌ | string | Local storage path |
| `custom_dimensions` | ❌ | object | Custom dimensions for logs |

#### Azure Blob Storage Listener
```json
{
    "azure_blob": {
        "enabled": true,
        "connection_string_secret": "blob-storage-connection-string",
        "container_name": "application-logs",
        "folder_structure": "{year}/{month}/{day}",
        "file_prefix": "app_log",
        "file_extension": ".json",
        "max_file_size_mb": 100,
        "retention_days": 90,
        "compression": {
            "enabled": true,
            "type": "gzip",
            "min_size_mb": 10
        },
        "metadata": {
            "environment": "${ENVIRONMENT}",
            "service": "${SERVICE_NAME}"
        }
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `enabled` | ✅ | boolean | Enable/disable the listener |
| `connection_string_secret` | ✅ | string | Secret name for connection string |
| `container_name` | ✅ | string | Blob container name |
| `folder_structure` | ❌ | string | Folder structure template (default: "{year}/{month}/{day}") |
| `file_prefix` | ❌ | string | Log file prefix (default: "log") |
| `file_extension` | ❌ | string | Log file extension (default: ".json") |
| `max_file_size_mb` | ❌ | number | Maximum file size in MB (default: 100) |
| `retention_days` | ❌ | number | Log retention period in days |
| `compression.enabled` | ❌ | boolean | Enable compression (default: false) |
| `compression.type` | ❌ | string | Compression type ("gzip") |
| `compression.min_size_mb` | ❌ | number | Minimum size for compression |
| `metadata` | ❌ | object | Custom metadata for blobs |

#### Console Listener
```json
{
    "console": {
        "enabled": true,
        "format": "{timestamp} [{level}] {message}",
        "colors": {
            "enabled": true,
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bold"
        },
        "level": "INFO",
        "show_source": true,
        "show_thread": true,
        "show_process": false,
        "timestamp_format": "%Y-%m-%d %H:%M:%S"
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `enabled` | ✅ | boolean | Enable/disable console logging |
| `format` | ❌ | string | Log message format template (default: "{timestamp} [{level}] {message}") |
| `colors.enabled` | ❌ | boolean | Enable colored output (default: true) |
| `colors.[LEVEL]` | ❌ | string | Color for each log level (supports "red", "green", "yellow", "blue", "magenta", "cyan", "white", "bold") |
| `level` | ❌ | string | Minimum log level (default: "INFO") |
| `show_source` | ❌ | boolean | Show source file and line (default: true) |
| `show_thread` | ❌ | boolean | Show thread name/id (default: true) |
| `show_process` | ❌ | boolean | Show process id (default: false) |
| `timestamp_format` | ❌ | string | Timestamp format string (default: "%Y-%m-%d %H:%M:%S") |

### Performance Configuration
```json
{
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
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `metrics_window_size` | ❌ | number | Size of metrics collection window (default: 1000) |
| `max_memory_mb` | ❌ | number | Maximum memory usage in MB (default: 1024) |
| `max_cpu_percent` | ❌ | number | Maximum CPU usage percentage (default: 80) |
| `max_disk_write_mbs` | ❌ | number | Maximum disk write speed in MB/s (default: 50) |
| `max_network_mbs` | ❌ | number | Maximum network usage in MB/s (default: 50) |
| `min_workers` | ❌ | number | Minimum worker threads (default: 2) |
| `max_workers` | ❌ | number | Maximum worker threads (default: 8) |
| `scale_up_threshold` | ❌ | number | Load threshold for scaling up (default: 0.75) |
| `scale_down_threshold` | ❌ | number | Load threshold for scaling down (default: 0.25) |

### Cache Configuration
```json
{
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
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `memory.enabled` | ❌ | boolean | Enable memory cache (default: true) |
| `memory.max_size_mb` | ❌ | number | Maximum memory cache size in MB (default: 100) |
| `memory.max_items` | ❌ | number | Maximum items in memory cache (default: 10000) |
| `memory.ttl_seconds` | ❌ | number | Memory cache TTL in seconds (default: 300) |
| `disk.enabled` | ❌ | boolean | Enable disk cache (default: true) |
| `disk.cache_dir` | ❌ | string | Disk cache directory |
| `disk.max_size_mb` | ❌ | number | Maximum disk cache size in MB (default: 1024) |
| `disk.ttl_seconds` | ❌ | number | Disk cache TTL in seconds (default: 86400) |

### Security Configuration
```json
{
    "security": {
        "encryption": {
            "enabled": true,
            "key_rotation_days": 30
        }
    }
}
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `encryption.enabled` | ❌ | boolean | Enable encryption (default: true) |
| `encryption.key_rotation_days` | ❌ | number | Key rotation period in days (default: 30) |

## Environment Variables

### Required Variables
- `AZURE_KEY_VAULT_URL`: Azure Key Vault URL
- `LOG_CACHE_DIR`: Directory for disk cache
- `ENVIRONMENT`: Environment name (e.g., "production", "staging")
- `SERVICE_NAME`: Service identifier

### Optional Variables
- `SERVICE_VERSION`: Service version
- Cloud provider authentication variables (based on provider)

## Configuration Tips

1. **Security**:
   - Always use key vault for sensitive information
   - Use environment variables for dynamic values
   - Enable encryption in production

2. **Performance**:
   - Adjust cache sizes based on available resources
   - Monitor and tune worker counts
   - Set appropriate file size limits

3. **Maintenance**:
   - Configure reasonable retention periods
   - Set up log rotation
   - Enable compression for large logs

4. **Best Practices**:
   - Start with default values
   - Monitor performance metrics
   - Adjust based on usage patterns
