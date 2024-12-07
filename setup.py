from setuptools import setup, find_packages

setup(
    name="skyarclog",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-json-logger>=2.0.7",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
    ],
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
    entry_points={
        'skyarclog.listeners': [
            'console = skyarclog.listeners.console.console_listener:ConsoleListener',
            'file = skyarclog.listeners.file.file_listener:FileListener',
            'azure_blob = skyarclog.listeners.azure.azure_blob_listener:AzureBlobListener [azure]',
            'azure_appinsights = skyarclog.listeners.azure.azure_appinsights_listener:AzureAppInsightsListener [azure]',
            'ms_sql = skyarclog.listeners.sql.mssql_listener:MsSqlListener [sql]',
        ],
        'skyarclog.transformers': [
            'json = skyarclog.transformers.json.json_transformer:JsonTransformer',
            'sql = skyarclog.transformers.sql.sql_transformer:SqlTransformer [sql]',
            'protobuf = skyarclog.transformers.protobuf.protobuf_transformer:ProtobufTransformer [protobuf]',
        ],
    },
    python_requires=">=3.8",
    description="A modular, cloud-agnostic logging framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/skyarclog",
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
