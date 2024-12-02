# Advanced Logging Framework

A powerful, flexible, and easy-to-use Python logging framework with support for multiple output formats and cloud integrations.

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install advanced-logging-framework

# Install with database support
pip install advanced-logging-framework[mysql]      # MySQL support
pip install advanced-logging-framework[postgresql] # PostgreSQL support
pip install advanced-logging-framework[mongodb]    # MongoDB support

# Install with cloud support
pip install advanced-logging-framework[azure]  # Azure support
pip install advanced-logging-framework[aws]    # AWS support
pip install advanced-logging-framework[gcp]    # Google Cloud support

# Install everything
pip install advanced-logging-framework[all]
```

### Basic Usage

```python
from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import ConsoleListener, FileListener

# Get the logging manager (singleton)
log_manager = LogManager.get_instance()

# Add formatters and listeners
log_manager.add_formatter(JSONFormatter())
log_manager.add_listener(ConsoleListener())
log_manager.add_listener(FileListener("app.log"))

# Start logging!
log_manager.info("Application started")
log_manager.error("Something went wrong", {"error_code": 500})
```

## 📋 Features

- **Multiple Output Formats**
  - Text (plain text)
  - JSON
  - XML
  - CSV

- **Various Output Destinations**
  - Console
  - Files
  - Databases (SQLite, MySQL, PostgreSQL, MongoDB)
  - Cloud Services (Azure, AWS, Google Cloud)

- **Easy Configuration**
  - Environment variables
  - JSON configuration files
  - Programmatic setup

- **Thread-Safe**
  - Safe for use in multi-threaded applications

## 💡 Examples

### 1. Basic File Logging

```python
from advanced_logging import LogManager
from advanced_logging.formatters import TextFormatter
from advanced_logging.listeners import FileListener

log_manager = LogManager.get_instance()
log_manager.add_formatter(TextFormatter())
log_manager.add_listener(FileListener("app.log"))

log_manager.info("User logged in", {"user_id": 123})
```

### 2. JSON Logging to Console

```python
from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import ConsoleListener

log_manager = LogManager.get_instance()
log_manager.add_formatter(JSONFormatter())
log_manager.add_listener(ConsoleListener())

log_manager.debug("Processing request", {
    "request_id": "abc-123",
    "method": "GET",
    "path": "/api/users"
})
```

### 3. Database Logging (PostgreSQL)

```python
from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import PostgreSQLListener

log_manager = LogManager.get_instance()
log_manager.add_formatter(JSONFormatter())
log_manager.add_listener(PostgreSQLListener(
    host="localhost",
    user="myuser",
    password="mypassword",
    database="myapp"
))

log_manager.error("Database connection failed", {
    "error_code": "DB_001",
    "retry_count": 3
})
```

### 4. Cloud Logging (AWS CloudWatch)

```python
from advanced_logging import LogManager
from advanced_logging.formatters import JSONFormatter
from advanced_logging.listeners import CloudWatchListener

log_manager = LogManager.get_instance()
log_manager.add_formatter(JSONFormatter())
log_manager.add_listener(CloudWatchListener(
    log_group="MyApp",
    log_stream="Production",
    region="us-west-2"
))

log_manager.warning("High CPU usage", {
    "cpu_percent": 85,
    "memory_available": "512MB"
})
```

## 🔧 Configuration

### Using Environment Variables

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Configure file output
export LOG_FILE_PATH=/var/log/myapp.log

# Database configuration
export LOG_DB_HOST=localhost
export LOG_DB_USER=myuser
export LOG_DB_PASSWORD=mypassword
```

### Using JSON Configuration

```json
{
  "log_level": "INFO",
  "formatters": ["json"],
  "listeners": {
    "console": true,
    "file": {
      "path": "app.log",
      "rotate": true,
      "max_size": "10MB"
    },
    "database": {
      "type": "postgresql",
      "host": "localhost",
      "user": "myuser",
      "password": "mypassword",
      "database": "myapp"
    }
  }
}
```

## 📝 Log Levels

The framework supports standard Python logging levels:

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Indicate a potential problem
- `ERROR`: A more serious problem
- `CRITICAL`: A critical problem that may prevent the program from running

## 🔒 Security Best Practices

1. **Never log sensitive information**
   ```python
   # ❌ Bad
   log_manager.info("User login", {"password": "secret123"})
   
   # ✅ Good
   log_manager.info("User login successful", {"user_id": 123})
   ```

2. **Use environment variables for credentials**
   ```python
   # ❌ Bad
   listener = PostgreSQLListener(password="mypassword")
   
   # ✅ Good
   import os
   listener = PostgreSQLListener(password=os.getenv("DB_PASSWORD"))
   ```

3. **Mask sensitive data**
   ```python
   # Log with masked credit card
   log_manager.info("Payment processed", {
       "card": "****-****-****-1234",
       "amount": 99.99
   })
   ```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Need Help?

- Check our [FAQ](FAQ.md)
- Open an [Issue](https://github.com/yourusername/advanced-logging/issues)
- Read our [Wiki](https://github.com/yourusername/advanced-logging/wiki)

## 🌟 Star the Project

If you find this logging framework useful, please give it a star on GitHub! It helps others discover the project.
