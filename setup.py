"""
Setup configuration for skyarclog package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("skyarclog/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="skyarclog",
    version="1.0.0",
    author="Krishna Kireeti Kompella",
    author_email="kireeti.k.k@gmail.com",
    description="A comprehensive logging framework with multiple formatters and listeners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kireeti123/skyarclog",
    packages=find_packages(),
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
    install_requires=requirements,
    extras_require={
        'mysql': ['mysql-connector-python>=8.0.26'],
        'postgresql': ['psycopg2-binary>=2.9.1'],
        'mongodb': ['pymongo>=3.12.0'],
        'azure': ['azure-monitor-opentelemetry>=1.0.0', 'opentelemetry-api>=1.10.0', 'opentelemetry-sdk>=1.10.0'],
        'aws': ['boto3>=1.18.0'],
        'gcp': ['google-cloud-logging>=3.0.0'],
        'all': [
            'mysql-connector-python>=8.0.26',
            'psycopg2-binary>=2.9.1',
            'pymongo>=3.12.0',
            'azure-monitor-opentelemetry>=1.0.0',
            'opentelemetry-api>=1.10.0',
            'opentelemetry-sdk>=1.10.0',
            'boto3>=1.18.0',
            'google-cloud-logging>=3.0.0',
            'uvloop>=0.16.0'
        ]
    }
)
