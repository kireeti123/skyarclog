"""
Setup configuration for skyarclog package.
"""

import os
import json
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Run parent install first
        install.run(self)
        
        # Get the package's config directory
        package_config_dir = os.path.join(os.path.dirname(__file__), 'skyarclog', 'config')
        default_config_file = os.path.join(package_config_dir, 'logging_config.json')
        
        # Create logging_config.json in the current directory if it doesn't exist
        target_config_file = "logging_config.json"
        if not os.path.exists(target_config_file):
            shutil.copy2(default_config_file, target_config_file)
            print(f"Created default {target_config_file} in the current directory")

setup(
    name="skyarclog",
    version="1.0.0",
    author="Krishna Kireeti Kompella",
    author_email="kireeti.k.k@gmail.com",
    description="A comprehensive logging framework with centralized key vault-based connection management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kireeti123/skyarclog",
    packages=find_packages(include=['skyarclog', 'skyarclog.*']),
    package_data={
        'skyarclog': ['config/*.json', 'config/*.md'],
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
    install_requires=requirements,
    cmdclass={
        'install': PostInstallCommand,
    },
    extras_require={
        'azure': [
            'azure-identity>=1.12.0',
            'azure-keyvault-secrets>=4.7.0',
            'azure-storage-blob>=12.16.0',
            'opencensus-ext-azure>=1.1.9',
        ],
        'aws': [
            'boto3>=1.26.0'
        ],
        'google': [
            'google-cloud-secret-manager>=2.16.0'
        ],
        'all': [
            'azure-identity>=1.12.0',
            'azure-keyvault-secrets>=4.7.0',
            'azure-storage-blob>=12.16.0',
            'opencensus-ext-azure>=1.1.9',
            'boto3>=1.26.0',
            'google-cloud-secret-manager>=2.16.0'
        ]
    }
)
