from setuptools import setup, find_packages

setup(
    name="skyarclog-azure-sql",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "skyarclog-core>=0.1.0",
        "pyodbc>=4.0.39"
    ],
    entry_points={
        'skyarclog.listeners': [
            'azure_sql = skyarclog_azure_sql.listener:AzureSqlListener'
        ]
    },
    python_requires=">=3.8"
)
