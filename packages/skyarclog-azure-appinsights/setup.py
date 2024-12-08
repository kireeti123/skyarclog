from setuptools import setup, find_packages

setup(
    name="skyarclog-azure-appinsights",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "skyarclog-core>=0.1.0",
        "azure-monitor-opentelemetry>=1.0.0",
        "opencensus-ext-azure>=1.1.9"
    ],
    entry_points={
        'skyarclog.listeners': [
            'azure_appinsights = skyarclog_azure_appinsights.listener:AzureAppInsightsListener'
        ]
    },
    python_requires=">=3.8"
)
