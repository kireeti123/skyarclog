# SkyArcLog - Advanced Logging Framework

A secure and efficient logging framework with built-in encryption, signature validation, and support for multiple output destinations including Azure services.

## Features

### 1. Core Logging Features
- Environment-based configuration
- Flexible setup mechanism
- Multiple output formats (JSON, plain text)
- Comprehensive error handling
- Performance optimized

### 2. Security
- AES-GCM encryption
- Log signatures
- Validation chain mechanism
- Key rotation support
- Secure configuration handling

### 3. Output Destinations
- Console logging
- File logging with rotation
- SQL Databases:
  - PostgreSQL
  - MySQL
  - MSSQL
  - SQLite
- Azure Integration (Optional):
  - Azure Application Insights
  - Azure Blob Storage

### 4. Configuration Management
- Environment-specific configurations
- Multiple configuration locations:
  - Package config
  - User home directory
  - Current working directory
- Environment variable substitution
- Secure credential handling

## Installation

You can install SkyArcLog using pip:

1. Basic Installation (Core Features):
```bash
pip install skyarclog
```

2. Install with Azure Support:
```bash
pip install skyarclog[azure]
```

3. Development Installation:
```bash
# Clone the repository
git clone https://github.com/kireeti123/skyarclog.git
cd skyarclog

# Install in editable mode
pip install -e .
```

### Prerequisites
- Python 3.7 or higher
- For Azure features:
  - Valid Azure subscription
  - Azure credentials

### Environment Variables
Required environment variables for Azure integration:

```bash
# Azure Application Insights
export AZURE_CONNECTION_STRING="your-connection-string"
export AZURE_INSTRUMENTATION_KEY="your-instrumentation-key"

# Azure Blob Storage
export AZURE_BLOB_CONNECTION_STRING="your-blob-connection-string"
```

## Usage

### Basic Setup

```python
from skyarclog import setup_logging

# Initialize logging with environment
logger = setup_logging("dev")  # or "prod", "azure"
log = logger.get_logger()

# Basic logging
log.info("Application started", extra={
    "version": "1.0.0",
    "environment": "development"
})

# Structured logging
log.info("User action", extra={
    "user_id": "12345",
    "action": "login",
    "ip_address": "192.168.1.1"
})

# Error logging with context
try:
    raise ValueError("Invalid input")
except Exception as e:
    log.exception("Error occurred", extra={
        "operation": "data_processing",
        "error_type": type(e).__name__
    })
```

### Configuration

Create a `custom_logging_dev.json` file:

```json
{
    "application": {
        "name": "your-app",
        "version": "1.0.0",
        "environment": "development"
    },
    "log_level": "INFO",
    "formatters": ["json"],
    "security": {
        "encryption": {
            "enabled": true,
            "type": "aes-gcm",
            "key_rotation_interval": "1d"
        },
        "signatures": {
            "enabled": true,
            "key_rotation_interval": "7d"
        }
    },
    "listeners": {
        "console": {
            "enabled": true,
            "format": "json"
        },
        "file": {
            "enabled": true,
            "path": "logs/app.log",
            "max_size": "100MB",
            "backup_count": 5
        }
    }
}
```

## Examples

Check the `examples` directory for more detailed examples:

1. `basic_logging/` - Basic logging setup and usage
2. `secure_logging/` - Encryption and signature examples
3. `database_logging/` - SQL database integration
4. `azure_logging/` - Azure integration examples

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
