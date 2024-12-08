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
- setuptools >= 61.0

### Install from GitHub

```bash
# Basic installation
pip install git+https://github.com/kireeti123/skyarclog.git

# Install with specific features
pip install git+https://github.com/kireeti123/skyarclog.git#egg=skyarclog[azure]
pip install git+https://github.com/kireeti123/skyarclog.git#egg=skyarclog[sql]
pip install git+https://github.com/kireeti123/skyarclog.git#egg=skyarclog[all]
```

### Troubleshooting Installation

If you encounter `ModuleNotFoundError: No module named 'pkg_resources'`:

1. Upgrade pip and setuptools:
```bash
pip install --upgrade pip setuptools wheel
```

2. Ensure you have the latest version of the package:
```bash
pip install --upgrade git+https://github.com/kireeti123/skyarclog.git
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/kireeti123/skyarclog.git
cd skyarclog

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode
pip install -e .
```

## Quick Start

### Basic Usage

#### Simple Logging

```python
import skyarclog

# Log a simple message
skyarclog.log('INFO', 'Hello, SkyArcLog!')

# Log with additional context
skyarclog.log('WARNING', 'Processing error', 
              extra={'user_id': 123, 'operation': 'data_sync'})
```

#### Configuration

```python
import skyarclog

# Configure logging with a custom configuration file
skyarclog.configure('/path/to/custom/config.json')

# Log messages after configuration
skyarclog.log('ERROR', 'Critical system error')
```

## Advanced Configuration

### Configuration Keys

The SkyArcLog framework supports a flexible JSON-based configuration with the following top-level keys:

- `version`: Configuration version (currently `1.0`)
- `name`: Application name (optional, defaults to 'Application')
- `transformers`: Message transformation configurations
- `listeners`: Log destination and output configurations
- `loggers`: Logger-specific settings

#### Example Configuration

```json
{
    "version": 1.0,
    "name": "MyApplication",
    "transformers": {
        "json": {
            "type": "json",
            "indent": 2
        }
    },
    "listeners": {
        "console": {
            "type": "console",
            "level": "INFO"
        },
        "azure_blob": {
            "type": "azure_blob",
            "connection_string": "${AZURE_STORAGE_CONNECTION_STRING}",
            "container_name": "applogs"
        }
    },
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": ["console", "azure_blob"]
        }
    }
}
```

## Core Components

### Plugin Management

SkyArcLog uses a plugin-based architecture for extensibility:

```python
from skyarclog.core import PluginManager

# Access the plugin manager (typically used internally)
plugin_manager = PluginManager()
```

## Listeners

SkyArcLog supports multiple log listeners:

- Console Listener
- Azure Blob Storage Listener
- Azure App Insights Listener
- SQL Listener (MS SQL)

### Adding Custom Listeners

You can extend the framework by creating custom listeners that implement the `BaseListener` interface.

## Security Considerations

- Use environment variables for sensitive information
- Recommended to use Azure Key Vault for secret management
- Avoid hardcoding credentials in configuration files

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you've installed the package with the correct optional dependencies
2. **Configuration Errors**: Validate your JSON configuration file
3. **Listener Plugins**: Make sure required dependencies are installed for specific listeners

## Performance and Scalability

- Lightweight, minimal overhead logging framework
- Supports buffered and asynchronous logging
- Configurable log levels and transformers

## Repository Structure

### `.gitignore`

The project includes a comprehensive `.gitignore` file that covers:
- Python-specific ignores
  - `__pycache__/`
  - `*.py[cod]`
- Distribution and packaging files
  - `dist/`
  - `build/`
  - `*.egg-info/`
- Virtual environments
  - `venv/`
  - `.env/`
- IDE-specific files
  - `.idea/`
  - `.vscode/`
- Logging and temporary files
  - `*.log`
  - `*.tmp`
- Operating system files
  - `.DS_Store`
  - `Thumbs.db`
- Testing and coverage files
  - `.coverage`
  - `htmlcov/`
- Sensitive configuration files
  - `*.env`
  - `*.secret`

### Project Layout

```
skyarclog/
│
├── src/
│   └── skyarclog/
│       ├── __init__.py
│       ├── logger.py
│       ├── config_manager.py
│       │
│       ├── listeners/
│       │   ├── base_listener.py
│       │   └── console/
│       │       └── console_listener.py
│       │
│       └── transformers/
│           ├── __init__.py
│           ├── base_transformer.py
│           ├── text_transformer.py
│           └── json_transformer.py
│
├── tests/
│   └── ... (test files)
│
├── examples/
│   └── ... (example usage scripts)
│
├── .gitignore
├── pyproject.toml
└── README.md
```

## Contributing

### Getting Started
1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Run tests
6. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation
- Ensure all tests pass before submitting a PR

### Reporting Issues
- Use GitHub Issues
- Provide a clear and descriptive title
- Include steps to reproduce the issue
- Share relevant code snippets or configuration

## License

[Specify your license here]

## Configuration Reference

#### Top-Level Configuration Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | Number | Optional | `1.0` | Configuration version |
| `name` | String | Optional | `"Application"` | Optional application name for identification (not used as a default logger name) |
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
5. The `name` field is purely for identification and documentation purposes
6. It does not set a default name for the root logger
7. Listener names are used as unique identifiers in the configuration

## Configuration Keys Deep Dive

#### Top-Level Keys

1. **`version`**
   - Purpose: Tracks configuration schema version
   - Type: Number
   - Default: `1.0`
   - Usage: Helps manage configuration compatibility
   - Example: 
     ```json
     {
         "version": 1.1
     }
     ```

2. **`name`**
   - Purpose: Application identification
   - Type: String
   - Default: `"Application"`
   - Usage: Purely descriptive, no functional impact
   - Example:
     ```json
     {
         "name": "MyWebApplication"
     }
     ```

3. **`transformers`**
   - Purpose: Define data transformation rules
   - Type: Object
   - Default: `{}`
   - Nested Keys:
     - Transformer Name (e.g., `"json_transformer"`)
       - `type`: Transformation type (`"json"`, `"sql"`)
       - `config`: Transformation-specific settings
   - Example:
     ```json
     {
         "transformers": {
             "json_transformer": {
                 "type": "json",
                 "config": {
                     "timestamp_format": "%Y-%m-%d %H:%M:%S",
                     "include_fields": ["message", "level"]
                 }
             }
         }
     }
     ```

4. **`listeners`**
   - Purpose: Configure log output destinations
   - Type: Object
   - Default: `{}`
   - Nested Keys:
     - Listener Name (e.g., `"console_log"`)
       - `type`: Listener type (`"console"`, `"azure-blob"`)
       - `enabled`: Whether listener is active
       - `transformer`: Optional transformer name
       - Listener-specific configuration
   - Example:
     ```json
     {
         "listeners": {
             "primary_console": {
                 "type": "console",
                 "enabled": true,
                 "transformer": "json_transformer",
                 "colors": {
                     "enabled": true,
                     "ERROR": "red,bold"
                 },
                 "show_timestamp": true,
                 "show_level": true
             }
         }
     }
     ```

5. **`loggers`**
   - Purpose: Define logging behavior
   - Type: Object
   - **Required Key**: `root`
   - Nested Keys for `root`:
     - `level`: Minimum log level
     - `handlers`: Log destinations per level
   - Example:
     ```json
     {
         "loggers": {
             "root": {
                 "level": "WARNING",
                 "handlers": {
                     "DEBUG": ["debug_listener"],
                     "ERROR": ["console", "azure-blob"]
                 }
             }
         }
     }
     ```

#### Configuration Hierarchy and Precedence

1. Top-level keys are processed in this order:
   - `version`
   - `name`
   - `transformers`
   - `listeners`
   - `loggers`

2. Level-specific handler routing allows granular control:
   ```json
   {
       "loggers": {
           "root": {
               "level": "WARNING",
               "handlers": {
                   "DEBUG": ["debug_log"],      // Only for DEBUG
                   "ERROR": ["error_log"],      // Only for ERROR
                   "WARNING": ["console"]       // Fallback for WARNING
               }
           }
       }
   }
   ```

#### Best Practices

- Use meaningful, unique names for transformers and listeners
- Keep sensitive information out of configuration files
- Use environment variables or secret management for credentials
- Validate configuration before deployment
- Use the latest `version` for newest features

#### Security Considerations

- Listener connection strings should use environment variables
- Never commit sensitive information to version control
- Use Azure Key Vault or similar secure secret management

Example with Environment Variables:
```json
{
    "listeners": {
        "azure_blob": {
            "type": "azure-blob",
            "container_connection_string": "@secret:AZURE_STORAGE_CONNECTION_STRING"
        }
    }
}
```

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/your-org/skyarclog](https://github.com/your-org/skyarclog)
