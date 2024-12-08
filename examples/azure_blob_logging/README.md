# Azure Blob Logging Example

## Prerequisites
- Python 3.8+
- Azure Storage Account
- Azure Blob Storage Connection String

## Setup Instructions

1. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies
```bash
pip install -e ../..  # Install skyarclog from the parent directory
pip install python-dotenv
```

3. Configure Azure Connection
- Copy `.env.example` to `.env`
- Replace `AZURE_STORAGE_CONNECTION_STRING` with your actual Azure Storage connection string

4. Run the example
```bash
python azure_blob_logging_example.py
```

## Configuration Details
- Logs will be stored in Azure Blob Storage
- Buffering is enabled with:
  - Max buffer size: 1000 messages
  - Flush interval: 60 seconds
  - Batch size: 100 messages
- Logs are compressed and stored in a structured folder: `{year}/{month}/{day}/{hour}`

## Troubleshooting
- Ensure Azure Storage connection string is correct
- Check network connectivity
- Verify Azure Storage account permissions
