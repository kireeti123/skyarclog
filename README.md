# SkyArcLog: Advanced Modular Logging Framework

## Overview

SkyArcLog is a powerful, flexible, and extensible logging framework designed to provide comprehensive logging capabilities for modern Python applications. It offers dynamic handler routing, configurable log levels, and support for multiple output destinations.

## Key Features

- 🌈 **Flexible Configuration**: Support for list and dictionary-based handler configurations
- 🔍 **Dynamic Log Routing**: Level-specific handler assignment
- 🚀 **Multiple Listeners**: Supports console, file, Azure Blob, Azure App Insights, and more
- 🔒 **Security-First**: Built-in encryption and key rotation
- 🌐 **Transformer Support**: JSON, SQL, and Protobuf transformers
- 🔧 **Highly Configurable**: Granular control over log formatting, colors, and output

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install via pip

```bash
pip install skyarclog
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/your-org/skyarclog.git

# Navigate to the project directory
cd skyarclog

# Install in editable mode
pip install -e .
```

## Quick Start

### Basic Configuration

Create a `skyarclog_logging.json` configuration file:

```json
{
    "version": 1.0,
    "name": "My Application",
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": {
                "DEBUG": ["console"],
                "INFO": ["console"],
                "WARNING": ["console"],
                "ERROR": ["console", "azure-blob"],
                "CRITICAL": ["console"]
            }
        }
    }
}
```

### Python Usage

```python
from skyarclog.logger import SkyArcLogger

# Initialize logger with configuration
logger = SkyArcLogger('path/to/skyarclog_logging.json')

# Log messages
logger.debug("Debug message")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Configuration Options

### Loggers

- `level`: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `handlers`: Specify handlers for different log levels
  - List mode: Apply same handlers to all levels
  - Dictionary mode: Level-specific handler routing

### Listeners

Supported listeners:
- `console`: Standard output logging
- `file`: File-based logging
- `azure-blob`: Azure Blob Storage logging
- `azure-appinsights`: Azure App Insights logging
- `ms-sql`: Microsoft SQL logging

### Transformers

- `json`: JSON formatting
- `sql`: SQL-compatible formatting
- `protobuf`: Protocol Buffers transformation

## Advanced Configuration

### Level-Specific Handlers

```json
{
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": {
                "DEBUG": ["console"],
                "ERROR": ["console", "azure-blob", "ms-sql"]
            }
        }
    }
}
```

### Security Configuration

```json
{
    "security": {
        "encryption": {
            "enabled": true,
            "type": "aes-gcm",
            "key_rotation_interval": "1d"
        }
    }
}
```

## Configuration Reference

#### Top-Level Configuration Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | Number | Optional | `1.0` | Configuration version |
| `name` | String | Optional | `"Application"` | Name of the application |
| `transformers` | Object | Optional | `{}` | Transformer configurations |
| `listeners` | Object | Optional | `{}` | Listener configurations |
| `loggers` | Object | **Required** | N/A | Logger configurations |

#### Loggers Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `root.level` | String | Optional | `"INFO"` | Global logging level. Allowed values: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |
| `root.handlers` | Object/List | Optional | `[]` | Log handlers for different log levels |

#### Listener Configuration

Each listener has its own specific configuration. Here are some common fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | Boolean | Optional | `true` | Whether the listener is active |
| `transformer` | String | Optional | `null` | Name of the transformer to use |

##### Console Listener Specific Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `output` | String | Optional | `"stdout"` | Output stream (`"stdout"` or `"stderr"`) |
| `colors.enabled` | Boolean | Optional | `true` | Enable colored output |
| `show_timestamp` | Boolean | Optional | `true` | Display timestamp in log |
| `show_level` | Boolean | Optional | `true` | Display log level |
| `show_thread` | Boolean | Optional | `true` | Display thread information |
| `show_process` | Boolean | Optional | `true` | Display process information |

##### Azure Blob Listener Specific Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `container_connection_string` | String | **Required** | Azure Storage connection string |
| `container_name` | String | **Required** | Name of the blob container |
| `folder_structure` | String | Optional | Custom folder structure for logs |
| `file_prefix` | String | Optional | Prefix for log files |
| `compression.enabled` | Boolean | Optional | Enable log file compression |

##### Azure App Insights Listener Specific Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrumentation_key` | String | **Required** | Azure App Insights instrumentation key |
| `enable_local_storage` | Boolean | Optional | Enable local storage for logs |

##### MS SQL Listener Specific Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `connection_string` | String | **Required** | SQL Database connection string |
| `table_name` | String | Optional | Custom table name for logs |
| `schema` | String | Optional | Database schema name |

#### Example of a Comprehensive Configuration

```json
{
    "version": 1.0,
    "name": "My Complex Application",
    "transformers": {
        "json_transformer": {
            "type": "json",
            "config": {
                "timestamp_format": "%Y-%m-%d %H:%M:%S",
                "include_fields": ["message", "level", "timestamp"]
            }
        }
    },
    "listeners": {
        "primary_console": {
            "type": "console",
            "enabled": true,
            "transformer": "json_transformer",
            "colors": {
                "enabled": true,
                "DEBUG": "cyan",
                "ERROR": "red,bold"
            },
            "show_timestamp": true,
            "show_level": true
        },
        "blob_backup": {
            "type": "azure-blob",
            "enabled": true,
            "container_connection_string": "YOUR_AZURE_CONNECTION_STRING",
            "container_name": "applogs",
            "compression": {
                "enabled": true
            }
        }
    },
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": {
                "DEBUG": ["primary_console"],
                "ERROR": ["primary_console", "blob_backup"]
            }
        }
    }
}
```

#### Notes on Configuration

1. The configuration supports both simple list-based and advanced dictionary-based handler routing.
2. Not all listeners need to be configured for every log level.
3. Listeners and transformers are optional but recommended for comprehensive logging.
4. Always keep sensitive information like connection strings secure and out of version control.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/your-org/skyarclog](https://github.com/your-org/skyarclog)
