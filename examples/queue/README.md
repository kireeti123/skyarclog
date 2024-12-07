# Queue Logging Example

This example demonstrates the asynchronous queue processing capabilities of SkyArcLog.

## Features Demonstrated

1. Asynchronous Processing
   - Multiple worker threads (2 workers in this example)
   - Non-blocking log operations
   - Batch processing of messages

2. Queue Management
   - Configurable queue size (1000 messages)
   - Batch processing (100 messages per batch)
   - Regular flush interval (1 second)
   
3. Error Handling
   - Automatic retries for failed messages
   - Configurable retry count and interval
   - Worker failure simulation

4. Monitoring
   - Queue statistics tracking
   - Worker thread status
   - Processing metrics

## Configuration Explanation

The `skyarclog_logging.json` file configures:

1. Queue Settings:
   ```json
   "queue": {
       "enabled": true,
       "queue_size": 1000,      // Maximum queued messages
       "batch_size": 100,       // Messages per batch
       "worker_count": 2,       // Number of worker threads
       "flush_interval": 1      // Seconds between flushes
   }
   ```

2. Retry Configuration:
   ```json
   "retry": {
       "enabled": true,
       "max_retries": 3,        // Maximum retry attempts
       "retry_interval": 1      // Seconds between retries
   }
   ```

3. Output Formatting:
   - Colored output with level-specific colors
   - Timestamp display
   - Worker thread identification
   - JSON formatting for extra fields

## Running the Example

```bash
python queue_logging_example.py
```

The example demonstrates:
1. High volume message processing
2. Worker failure handling and retries
3. Queue statistics monitoring
4. Batch processing behavior

Watch the output to see:
- Asynchronous message processing
- Worker thread activity
- Retry behavior on failures
- Queue statistics updates
