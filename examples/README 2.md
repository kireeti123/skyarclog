# Advanced Logging Framework Examples

This directory contains example code demonstrating various features of the Advanced Logging Framework.

## Directory Structure

```
examples/
├── basic_logging/
│   ├── config.json           # Basic configuration for console and file logging
│   └── basic_example.py      # Example using console and file listeners
├── database_logging/
│   ├── config.json           # Configuration for various database listeners
│   └── database_example.py   # Example using database listeners (SQLite, MySQL, etc.)
└── cloud_logging/
    ├── config.json           # Configuration for cloud service listeners
    └── cloud_example.py      # Example using cloud listeners (Azure, AWS, GCP)
```

## Basic Logging Example

Demonstrates basic logging functionality using console and file listeners. Features include:
- Colored console output
- File rotation
- Multiple formatters (JSON and Text)
- Different log levels with context

```bash
python basic_logging/basic_example.py
```

## Database Logging Example

Shows how to use various database listeners for log storage. Includes:
- SQLite for local storage
- MySQL and PostgreSQL for relational databases
- MongoDB for document storage
- Redis for high-speed caching
- Elasticsearch for full-text search
- Cassandra for distributed storage

```bash
python database_logging/database_example.py
```

## Cloud Logging Example

Demonstrates integration with major cloud providers:
- Azure Application Insights
- AWS CloudWatch
- Google Cloud Logging

Features:
- Structured logging
- Distributed tracing
- Custom attributes and dimensions
- Resource labeling

```bash
python cloud_logging/cloud_example.py
```

## Configuration

Each example includes a `config.json` file showing how to configure the logging framework. Key aspects:
- Log level configuration
- Formatter selection
- Listener-specific settings
- Authentication credentials (replace with your own)

## Prerequisites

1. Install the framework with all dependencies:
```bash
pip install advanced-logging-framework[all]
```

2. For database examples:
- Running database servers (MySQL, PostgreSQL, MongoDB, etc.)
- Proper credentials and permissions

3. For cloud examples:
- Cloud provider accounts
- API keys or credentials
- Proper IAM/role configurations

## Security Note

The configuration files contain placeholder credentials. In a production environment:
- Never commit real credentials to version control
- Use environment variables or secure credential stores
- Follow security best practices for each service

## Additional Resources

- [Framework Documentation](../README.md)
- [API Reference](../docs/api.md)
- [Configuration Guide](../docs/configuration.md)
