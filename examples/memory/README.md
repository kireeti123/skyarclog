# Memory Logging Example

This example demonstrates the memory buffering capabilities of SkyArcLog.

## Features Demonstrated

1. Message Buffering
   - Low priority messages (DEBUG/INFO) are buffered in memory
   - Warnings are displayed immediately
   - Buffer size is configurable (1000 messages in this example)

2. Flush Triggers
   - Level-based: Messages at ERROR or above trigger immediate flush
   - Capacity-based: Buffer flushes when full (1000 messages)
   - Time-based: Regular flush every 5 seconds
   
3. Configuration Options
   - Buffer capacity
   - Flush level threshold
   - Flush interval
   - Target handlers for flushed messages

## Configuration Explanation

The `skyarclog_logging.json` file configures:

1. Memory Listener Settings:
   ```json
   "memory": {
       "enabled": true,
       "capacity": 1000,        // Maximum messages before flush
       "flush_level": "ERROR",  // Level that triggers flush
       "flush_interval": 5,     // Seconds between auto-flush
       "flush_on_capacity": true
   }
   ```

2. Output Formatting:
   - Colored output
   - Timestamp display
   - JSON formatting for extra fields

## Running the Example

```bash
python memory_logging_example.py
```

The example demonstrates:
1. Buffering of low priority messages
2. Immediate flush on error
3. Capacity-based flush
4. Time-based flush

Watch the output to see how different types of messages are handled and when the buffer is flushed.
