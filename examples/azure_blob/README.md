# Azure Blob Storage Logging Example

This example demonstrates how to use SkyArcLog with Azure Blob Storage for persistent log storage.

## Features Demonstrated

1. Structured Logging
   - Session tracking
   - User activity monitoring
   - Batch processing logs
   - Progress tracking

2. Azure Blob Integration
   - Hierarchical blob storage (year/month/day/hour)
   - Batch uploads
   - Automatic retries
   - Connection string configuration
   
3. Metadata Management
   - Application identification
   - Environment tagging
   - Custom metadata fields

## Configuration Explanation

The `skyarclog_logging.json` file configures:

1. Azure Blob Settings:
   ```json
   "azure_blob": {
       "enabled": true,
       "connection_string": "${AZURE_STORAGE_CONNECTION_STRING}",
       "container_name": "application-logs",
       "blob_prefix": "logs/%Y/%m/%d/%H/",
       "blob_extension": ".json"
   }
   ```

2. Batch Processing:
   ```json
   "batch_size": 100,
   "flush_interval": 60,
   "retry": {
       "enabled": true,
       "max_retries": 3
   }
   ```

3. Metadata Configuration:
   ```json
   "metadata": {
       "application": "skyarclog-example",
       "environment": "development"
   }
   ```

## Prerequisites

1. Azure Storage Account
   - Create a storage account in Azure
   - Create a container named "application-logs"
   - Get the connection string

2. Environment Setup
   ```bash
   export AZURE_STORAGE_CONNECTION_STRING="your_connection_string_here"
   ```

## Running the Example

```bash
python azure_blob_logging_example.py
```

The example demonstrates:
1. Application activity logging with session tracking
2. Batch processing with progress updates
3. Automatic blob storage organization

## Viewing the Logs

Logs will be stored in your Azure Storage account with the following structure:
```
application-logs/
    logs/
        2024/
            01/
                15/
                    10/
                        log_xxx.json
```

You can use Azure Storage Explorer or the Azure Portal to view the logs.
