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
                "DEBUG": ["debug-listener"],
                "INFO": ["info-listener"],
                "WARNING": ["console"],
                "ERROR": ["console", "azure-blob"],
                "CRITICAL": ["critical-alert"]
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
                "DEBUG": ["debug-listener"],
                "ERROR": ["console", "azure-blob", "alert-system"]
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
