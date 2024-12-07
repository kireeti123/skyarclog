# Console Logging Example

This example demonstrates how to use SkyArcLog for console logging with colored output and JSON formatting.

## Configuration

The `skyarclog_logging.json` file contains a minimal configuration for console logging:
- JSON formatting with indentation and sorted keys
- Colored output for different log levels
- Timestamp display with customizable format
- Log level display

## Running the Example

1. Install SkyArcLog:
```bash
pip install skyarclog
```

2. Run the example:
```bash
python console_logging_example.py
```

## Expected Output

You should see colored log messages in the console with:
- Timestamp
- Log level
- Message
- Additional context in JSON format

Example output:
```
2024-01-20 10:30:45.123 DEBUG    {"component": "example", "message": "This is a debug message", "trace_id": "123"}
2024-01-20 10:30:45.124 INFO     {"message": "This is an info message", "user": "john_doe"}
2024-01-20 10:30:45.125 WARNING  {"message": "This is a warning message", "status_code": 404}
2024-01-20 10:30:45.126 ERROR    {"error_message": "division by zero", "error_type": "ZeroDivisionError", "message": "An error occurred"}
2024-01-20 10:30:45.127 CRITICAL {"action": "login", "message": "This is a critical message", "service": "authentication", "attempts": 3}
```

## Customization

You can modify `skyarclog_logging.json` to:
- Change color schemes
- Adjust timestamp format
- Configure JSON formatting options
- Add or remove displayed fields
