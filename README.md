# SkyArcLog

A comprehensive, secure, and high-performance logging framework for Python applications.

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install skyarclog

# Install with database support
pip install skyarclog[mysql]      # MySQL support
pip install skyarclog[postgresql] # PostgreSQL support
pip install skyarclog[mongodb]    # MongoDB support

# Install with cloud support
pip install skyarclog[azure]  # Azure support
pip install skyarclog[aws]    # AWS support
pip install skyarclog[gcp]    # Google Cloud support

# Install everything
pip install skyarclog[all]
```

### Basic Usage

```python
from skyarclog import LogManager
from skyarclog.formatters import JSONFormatter
from skyarclog.listeners import ConsoleListener, FileListener

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
from skyarclog import LogManager
from skyarclog.formatters import TextFormatter
from skyarclog.listeners import FileListener

log_manager = LogManager.get_instance()
log_manager.add_formatter(TextFormatter())
log_manager.add_listener(FileListener("app.log"))

log_manager.info("User logged in", {"user_id": 123})
```

### 2. JSON Logging to Console

```python
from skyarclog import LogManager
from skyarclog.formatters import JSONFormatter
from skyarclog.listeners import ConsoleListener

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
from skyarclog import LogManager
from skyarclog.formatters import JSONFormatter
from skyarclog.listeners import PostgreSQLListener

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
from skyarclog import LogManager
from skyarclog.formatters import JSONFormatter
from skyarclog.listeners import CloudWatchListener

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
- Open an [Issue](https://github.com/yourusername/skyarclog/issues)
- Read our [Wiki](https://github.com/yourusername/skyarclog/wiki)

## 🌟 Star the Project

If you find this logging framework useful, please give it a star on GitHub! It helps others discover the project.