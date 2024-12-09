# SkyArcLog: Advanced Modular Logging Framework

## Overview

SkyArcLog is a powerful, flexible, and extensible logging framework designed for modern Python applications. It provides dynamic configuration, pluggable components, and comprehensive logging capabilities with support for multiple output destinations and formats.

## Key Features

- 🔌 **Plugin Architecture**: Modular design with dynamic component loading
- 🎨 **Flexible Formatters**: Built-in support for JSON, SQL, and Protobuf formats
- 🎯 **Multiple Listeners**: Console, File, Azure services (Blob, App Insights, MS SQL)
- ⚙️ **Dynamic Configuration**: JSON-based configuration with environment variable support
- 🔒 **Secure by Design**: Best practices for credential management
- 🚀 **High Performance**: Asynchronous logging and buffering capabilities
- 🛠️ **Extensible**: Easy to add custom formatters and listeners

## Installation

### Requirements
- Python 3.8+
- pip
- setuptools >= 61.0

### Basic Installation

```bash
pip install skyarclog
```

### Feature-specific Installation

```bash
# Azure features (includes Blob Storage, App Insights, and MS SQL)
pip install skyarclog[azure]

# Protobuf support
pip install skyarclog[protobuf]

# All features
pip install skyarclog[all]
```

## Quick Start

### Basic Usage

```python
from skyarclog.logger import SkyArcLogger

# Initialize with config file
logger = SkyArcLogger("config.json")

# Log messages at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Log with additional context
logger.info("User login", extra={
    "user_id": "12345",
    "ip_address": "192.168.1.1",
    "status": "success"
})
```

## Configuration

### Basic Configuration Structure

```json
{
    "version": 1.0,
    "name": "MyApplication",
    "formatters": {
        "json": {
            "type": "json_formatter",
            "config": {
                "indent": 2,
                "sort_keys": true
            }
        }
    },
    "listeners": {
        "console": {
            "type": "console",
            "enabled": true,
            "level": "INFO",
            "formatter": "json"
        },
        "ms_sql": {
            "type": "azure_ms_sql",
            "enabled": true,
            "config": {
                "connection_string": "${AZURE_SQL_CONNECTION}",
                "table_name": "ApplicationLogs",
                "formatter": "sql"  // Uses the built-in SQL formatter
            }
        }
    },
    "loggers": {
        "root": {
            "level": "INFO",
            "handlers": ["console", "ms_sql"]
        }
    }
}
```

## Components

### Built-in Formatters

- **JSON Formatter**: Flexible JSON output with customizable indentation
- **SQL Formatter**: Built-in formatter for SQL storage (used by Azure MS SQL)
- **Protobuf Formatter**: Efficient binary format using Protocol Buffers
- **Text Formatter**: Simple text output (fallback formatter)

### Built-in Listeners

- **Console Listener**: Standard output logging
- **File Listener**: File-based logging with rotation support
- **Memory Listener**: In-memory logging for testing
- **Queue Listener**: Asynchronous logging via queue

### Azure Integration

The Azure package (`skyarclog[azure]`) provides the following components:

- **Azure MS SQL Listener**: Log to Azure SQL Database
  - Uses the built-in SQL formatter
  - Supports connection pooling and batching
  - Automatic reconnection handling

- **Azure Blob Listener**: Store logs in Azure Blob Storage
  - Configurable blob naming patterns
  - Support for container management
  - Automatic retry logic

- **Azure App Insights Listener**: Send telemetry to Azure Application Insights
  - Custom dimension support
  - Built-in performance metrics
  - Exception tracking

## Azure Integration Examples

### Azure MS SQL Configuration

```json
{
    "listeners": {
        "sql": {
            "type": "azure_ms_sql",
            "enabled": true,
            "config": {
                "connection_string": "${AZURE_SQL_CONNECTION}",
                "table_name": "logs",
                "batch_size": 100,
                "flush_interval": 30,
                "formatter": "sql"  // Uses the built-in SQL formatter
            }
        }
    }
}
```

### Azure Blob Storage Configuration

```json
{
    "listeners": {
        "blob": {
            "type": "azure_blob",
            "enabled": true,
            "config": {
                "connection_string": "${AZURE_STORAGE_CONNECTION}",
                "container_name": "logs",
                "blob_prefix": "app/{date}/"
            }
        }
    }
}
```

### Azure Application Insights Configuration

```json
{
    "listeners": {
        "appinsights": {
            "type": "azure_appinsights",
            "enabled": true,
            "config": {
                "instrumentation_key": "${APPINSIGHTS_KEY}",
                "buffer_size": 100
            }
        }
    }
}
```

## Best Practices

### Security
1. Use environment variables for sensitive information
2. Never commit configuration files with credentials
3. Use Azure Key Vault for secret management
4. Implement proper access controls for log storage

### Performance
1. Use appropriate log levels
2. Configure batch processing for database listeners
3. Implement log rotation for file-based logging
4. Use async listeners for high-throughput scenarios

### Configuration
1. Validate configurations before deployment
2. Use meaningful component names
3. Implement proper error handling
4. Set appropriate log levels for different environments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
