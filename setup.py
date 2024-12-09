from setuptools import setup, find_packages
import os

# Read the contents of README.md
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "SkyArcLog - A modular, cloud-agnostic logging framework"

setup(
    name="skyarclog",
    version="0.1.1",  # Increment version
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Ensure setuptools is a requirement
    setup_requires=[
        'setuptools>=61.0.0',
        'wheel',
    ],
    
    # Core dependencies
    install_requires=[
        'setuptools>=61.0.0',  # Explicitly include setuptools
        'python-json-logger>=2.0.7',
        'python-dotenv>=1.0.0',
        'colorama>=0.4.6',
        'packaging',  # Add packaging to resolve potential dependency issues
    ],
    
    # Optional dependencies
    extras_require={
        'azure': [
            'azure-storage-blob>=12.0.0',
            'opencensus-ext-azure>=1.1.9',
            'opencensus-ext-logging>=0.1.0',
            'azure-identity>=1.12.0',
            'azure-keyvault-secrets>=4.7.0',
        ],
        'sql': [
            'pyodbc>=4.0.39',
        ],
        'protobuf': [
            'protobuf>=4.21.0',
        ],
        'all': [
            'azure-storage-blob>=12.0.0',
            'opencensus-ext-azure>=1.1.9',
            'opencensus-ext-logging>=0.1.0',
            'azure-identity>=1.12.0',
            'azure-keyvault-secrets>=4.7.0',
            'pyodbc>=4.0.39',
            'protobuf>=4.21.0',
        ],
    },
    
    # Entry points for plugin discovery
    entry_points={
        'skyarclog.listeners': [
            'console = skyarclog.listeners.console.console_listener:ConsoleListener',
            'file = skyarclog.listeners.file.file_listener:FileListener',
            'azure_blob = skyarclog.listeners.azure.azure_blob_listener:AzureBlobListener [azure]',
            'azure_appinsights = skyarclog.listeners.azure.azure_appinsights_listener:AzureAppInsightsListener [azure]',
            'ms_sql = skyarclog.listeners.sql.mssql_listener:MsSqlListener [sql]',
        ],
        'skyarclog.formatters': [
            'json = skyarclog.formatters.json.json_formatter:JsonTransformer',
            'sql = skyarclog.formatters.sql.sql_formatter:SqlTransformer [sql]',
            'protobuf = skyarclog.formatters.protobuf.protobuf_formatter:ProtobufTransformer [protobuf]',
        ],
    },
    
    # Metadata
    python_requires=">=3.8",
    description="A modular, cloud-agnostic logging framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Krishna Kireeti",
    author_email="kireeti.kompella@example.com",
    url="https://github.com/kireeti123/skyarclog",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
