# Azure Application Insights Logging Example

This example demonstrates how to use SkyArcLog with Azure Application Insights for application telemetry and monitoring.

## Features Demonstrated

1. Request Telemetry
   - Web request tracking
   - Response time monitoring
   - Success/failure tracking
   - Client IP and user context

2. Dependency Tracking
   - Database calls
   - Cache operations
   - External API calls
   - Dependency timing
   
3. Custom Metrics
   - User session tracking
   - API response times
   - Business metrics
   - Custom dimensions

## Configuration Explanation

The `skyarclog_logging.json` file configures:

1. Application Insights Settings:
   ```json
   "app_insights": {
       "enabled": true,
       "instrumentation_key": "${APPINSIGHTS_INSTRUMENTATIONKEY}",
       "connection_string": "${APPLICATIONINSIGHTS_CONNECTION_STRING}",
       "batch_size": 100,
       "flush_interval": 30
   }
   ```

2. Telemetry Processing:
   ```json
   "telemetry_processor": {
       "sampling_percentage": 100,
       "exclude_types": ["DEBUG"]
   }
   ```

3. Context Configuration:
   ```json
   "config": {
       "cloud_role_name": "skyarclog-example",
       "cloud_role_instance": "${COMPUTERNAME}",
       "include_context": true
   }
   ```

## Prerequisites

1. Azure Application Insights
   - Create an Application Insights resource in Azure
   - Get the instrumentation key and connection string

2. Environment Setup
   ```bash
   export APPINSIGHTS_INSTRUMENTATIONKEY="your_instrumentation_key_here"
   export APPLICATIONINSIGHTS_CONNECTION_STRING="your_connection_string_here"
   ```

## Running the Example

```bash
python app_insights_logging_example.py
```

The example demonstrates:
1. Web request telemetry with timing and status
2. Dependency tracking for external services
3. Custom metric collection

## Viewing the Telemetry

1. Azure Portal
   - Go to your Application Insights resource
   - View the following sections:
     - Live Metrics
     - Transaction Search
     - Performance
     - Failures
     - Metrics Explorer

2. Available Data
   - Request metrics (count, duration, success rate)
   - Dependency metrics (calls, timing, failures)
   - Custom metrics (user sessions, business metrics)
   - Exception tracking
   - Custom events
