from setuptools import setup, find_packages

setup(
    name="skyarclog-azure-blob",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "skyarclog-core>=0.1.0",
        "azure-storage-blob>=12.0.0"
    ],
    entry_points={
        'skyarclog.listeners': [
            'azure_blob = skyarclog_azure_blob.listener:AzureBlobListener'
        ]
    },
    python_requires=">=3.8"
)
