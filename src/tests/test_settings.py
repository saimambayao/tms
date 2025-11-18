"""
Test settings for #FahanieCares project.
"""

from config.settings.base import *

# Override settings for testing
DEBUG = False
TESTING = True

# Use PostgreSQL test database for consistency
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('TEST_DB_NAME', 'fahaniecares_test_db'),
        'USER': os.environ.get('DB_USER', 'fahaniecares_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'changeme'),
        'HOST': os.environ.get('DB_HOST', 'db' if os.environ.get('DOCKER_ENV') else 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'fahaniecares_test_db',
        }
    }
}

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable rate limiting for tests
RATE_LIMIT_PER_MINUTE = 10000
MAX_LOGIN_ATTEMPTS = 100

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files for testing
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Notion test settings
NOTION_API_KEY = 'test_api_key'
NOTION_CONSTITUENT_DATABASE = 'test_constituent_db'
NOTION_SERVICE_APPLICATION_DB_ID = 'test_service_db'
NOTION_CHAPTER_DATABASE = 'test_chapter_db'