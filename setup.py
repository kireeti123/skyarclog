"""
Setup configuration for skyarclog package.
"""

from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Base requirements
base_requirements = [
    "redis>=4.5.0",
    "elasticsearch>=8.0.0",
    "cassandra-driver>=3.25.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "cryptography>=40.0.0",
    "typing>=3.7.4",
    "concurrent-log-handler>=0.9.20",
    "pymongo>=4.5.0",
    "PyMySQL>=1.1.0",
    "DBUtils>=3.0.3",
]

# Optional dependencies
extras_require = {
    'azure': [
        'azure-identity>=1.12.0',
        'azure-keyvault-secrets>=4.7.0',
        'azure-storage-blob>=12.16.0',
        'azure-core>=1.26.0',
        'opencensus-ext-azure>=1.1.9',
        'opencensus>=0.11.0',
        'opencensus-ext-logging>=0.1.0',
    ],
    'aws': [
        'boto3>=1.26.0'
    ],
    'google': [
        'google-cloud-secret-manager>=2.16.0'
    ],
    'mssql': [
        'pymssql>=2.2.0'  # Optional SQL Server support
    ]
}

# Add 'all' option that includes all extras
extras_require['all'] = [
    package
    for extra in extras_require.values()
    for package in extra
]

setup(
    name="skyarclog",
    version="1.0.0",
    author="Krishna Kireeti Kompella",
    author_email="kireeti.k.k@gmail.com",
    description="A comprehensive logging framework with centralized key vault-based connection management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kireeti123/skyarclog",
    project_urls={
        "Bug Tracker": "https://github.com/kireeti123/skyarclog/issues",
        "Documentation": "https://github.com/kireeti123/skyarclog#readme",
        "Source Code": "https://github.com/kireeti123/skyarclog",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        'skyarclog': [
            'config/*.json',
            'config/*.md',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=base_requirements,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'skyarclog=skyarclog.cli:main',
        ],
    },
)
