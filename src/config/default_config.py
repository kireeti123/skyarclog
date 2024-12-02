"""
Default configuration for skyarclog.
This module provides the default configuration that can be imported and modified as needed.
"""

import os
import logging

# Default logging configuration
DEFAULT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,  # Changed to True to disable existing loggers by default
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': os.path.join(os.getcwd(), 'skyarclog.log'),
            'mode': 'a'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'skyarclog': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Azure Key Vault configuration
AZURE_CONFIG = {
    'use_managed_identity': False,
    'tenant_id': None,
    'client_id': None,
    'client_secret': None,
    'vault_url': None
}

# AWS Secrets Manager configuration
AWS_CONFIG = {
    'region_name': None,
    'access_key_id': None,
    'secret_access_key': None
}

# Cache configuration
CACHE_CONFIG = {
    'enabled': True,
    'ttl': 3600,  # Time to live in seconds
    'max_size': 1000  # Maximum number of items in cache
}

# Monitoring configuration
MONITORING_CONFIG = {
    'enabled': True,
    'metrics_interval': 60,  # seconds
    'health_check_interval': 300  # seconds
}
