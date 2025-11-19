"""
Development settings for #BM Parliament project.
"""

import os
from dotenv import load_dotenv
from .base import *

# Load environment variables from .env file in the src/ directory
load_dotenv(os.path.join(BASE_DIR, '.env'))

print("DEBUG: development.py is being loaded.")
print(f"DEBUG: BASE_DIR: {BASE_DIR}")
print(f"DEBUG: STATICFILES_DIRS: {STATICFILES_DIRS}")
print(f"DEBUG: STATIC_URL: {STATIC_URL}")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Database configuration
# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Add development specific apps
INSTALLED_APPS += [
    # 'django_extensions',  # Commented out for now
]

# Development-specific middleware
MIDDLEWARE += [
    # Add any development-specific middleware here
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Override cache to use local memory cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# CSRF settings for development
# CSRF_TRUSTED_ORIGINS inherited from base.py with comprehensive coverage
# Additional development-specific overrides if needed
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access for development debugging


# Development-specific logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Celery configuration for development
# Using in-memory broker for local development without Redis
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+locmem://'
CELERY_ALWAYS_EAGER = True  # Execute tasks synchronously in development
