# MS SQL Server Logging Example

This example demonstrates how to use SkyArcLog with MS SQL Server for structured logging and analytics.

## Features Demonstrated

1. Application Event Logging
   - User activities
   - Transaction processing
   - Success/failure tracking
   - Processing time metrics

2. System Metrics
   - CPU utilization
   - Memory usage
   - Disk I/O
   - Performance tracking
   
3. Audit Logging
   - Security events
   - Configuration changes
   - Data access tracking
   - Change history

## Configuration Explanation

The `skyarclog_logging.json` file configures:

1. SQL Server Settings:
   ```json
   "mssql": {
       "enabled": true,
       "connection_string": "${MSSQL_CONNECTION_STRING}",
       "table_name": "application_logs",
       "batch_size": 100,
       "flush_interval": 30
   }
   ```

2. Database Schema:
   ```json
   "schema": {
       "event_id": "UNIQUEIDENTIFIER",
       "timestamp": "DATETIME2",
       "level": "VARCHAR(10)",
       "message": "NVARCHAR(MAX)",
       "event_type": "VARCHAR(50)",
       ...
   }
   ```

3. Performance Optimization:
   ```json
   "indexes": [
       {
           "name": "IX_timestamp",
           "columns": ["timestamp"]
       },
       ...
   ]
   ```

## Prerequisites

1. MS SQL Server
   - Create a database for logging
   - Create a user with appropriate permissions
   - Get the connection string

2. Environment Setup
   ```bash
   export MSSQL_CONNECTION_STRING="Server=server_name;Database=db_name;User Id=user;Password=password;"
   ```

## Running the Example

```bash
python mssql_logging_example.py
```

The example demonstrates:
1. Application event logging with context
2. System metric collection
3. Audit log generation

## Database Schema

The logs are stored in the `application_logs` table with the following structure:

```sql
CREATE TABLE application_logs (
    event_id UNIQUEIDENTIFIER,
    timestamp DATETIME2,
    level VARCHAR(10),
    message NVARCHAR(MAX),
    event_type VARCHAR(50),
    event_category VARCHAR(50),
    user_id VARCHAR(100),
    status VARCHAR(20),
    error_type VARCHAR(100),
    error_message NVARCHAR(MAX),
    processing_time FLOAT,
    metric_type VARCHAR(20),
    metric_value FLOAT,
    audit_id UNIQUEIDENTIFIER,
    admin_user VARCHAR(100),
    ip_address VARCHAR(50),
    affected_resource VARCHAR(200),
    change_details NVARCHAR(MAX)
);
```

## Querying the Logs

Example SQL queries for analysis:

1. Recent Error Events:
```sql
SELECT timestamp, event_type, error_message
FROM application_logs
WHERE level = 'ERROR'
ORDER BY timestamp DESC;
```

2. Performance Analysis:
```sql
SELECT 
    event_type,
    AVG(processing_time) as avg_time,
    COUNT(*) as total_events
FROM application_logs
WHERE status = 'success'
GROUP BY event_type;
```

3. Audit Trail:
```sql
SELECT 
    timestamp,
    action,
    admin_user,
    affected_resource,
    change_details
FROM application_logs
WHERE event_category = 'Security'
ORDER BY timestamp;
