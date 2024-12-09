from setuptools import setup, find_packages

setup(
    name="skyarclog-azure",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "skyarclog-core>=0.1.0",
        "azure-storage-blob>=12.0.0",
        "azure-monitor-opentelemetry>=1.0.0",
        "opencensus-ext-azure>=1.1.9",
        "pyodbc>=4.0.39"
    ],
    entry_points={
        'skyarclog.listeners': [
            'azure_appinsights = skyarclog_azure_appinsights.listener:AzureAppInsightsListener',
            'azure_blob = skyarclog_azure_blob.listener:AzureBlobListener',
            'azure_ms_sql = skyarclog_azure_ms_sql.listener:AzureMsSqlListener'
        ],
        'skyarclog.formatters': [
            'sql = skyarclog_azure_ms_sql.formatter:SqlFormatter'
        ]
    },
    author="Krishna Kireeti",
    author_email="kireeti.kompella@example.com",
    description="Azure integration package for SkyArcLog",
    long_description="Azure integration package for SkyArcLog including Blob Storage, MS SQL, and Application Insights support",
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
    python_requires=">=3.8"
)
