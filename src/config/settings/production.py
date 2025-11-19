"""
Production settings for #BM Parliament project.
"""

import os
import logging
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security settings
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production")

# Production domains
ALLOWED_HOSTS = [
    'bmparliament.ph',
    'www.bmparliament.ph',
    '.bmparliament.ph',  # Allow all subdomains
    'localhost',  # For health checks
    '127.0.0.1',  # For health checks
]

# Add Railway domains if provided
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')

if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
    ALLOWED_HOSTS.append(f'.{RAILWAY_PUBLIC_DOMAIN}')

if RAILWAY_STATIC_URL:
    ALLOWED_HOSTS.append(RAILWAY_STATIC_URL)

# Add Railway auto-generated domains (*.up.railway.app)
# Railway generates domains like: <service-name>.up.railway.app
ALLOWED_HOSTS.extend([
    '*.up.railway.app',  # All Railway auto-generated domains
    'up.railway.app',     # Base Railway domain
])

# Add any additional allowed hosts from environment
ADDITIONAL_ALLOWED_HOSTS = os.getenv('ADDITIONAL_ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS.extend([host.strip() for host in ADDITIONAL_ALLOWED_HOSTS if host.strip()])

# Remove duplicates
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Additional Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# SSL Certificate Configuration
SSL_CERTIFICATE_PATH = os.getenv('SSL_CERTIFICATE_PATH', '/etc/letsencrypt/live/bmparliament.ph/fullchain.pem')
SSL_PRIVATE_KEY_PATH = os.getenv('SSL_PRIVATE_KEY_PATH', '/etc/letsencrypt/live/bmparliament.ph/privkey.pem')

# Certificate Pinning (Optional - Use with caution)
ENABLE_CERTIFICATE_PINNING = os.getenv('ENABLE_CERTIFICATE_PINNING', 'False').lower() == 'true'
if ENABLE_CERTIFICATE_PINNING:
    # Add your certificate SHA256 pins here
    CERTIFICATE_PINS = [
        # Primary certificate pin
        os.getenv('PRIMARY_CERT_PIN', ''),
        # Backup certificate pin
        os.getenv('BACKUP_CERT_PIN', ''),
    ]
    HPKP_MAX_AGE = int(os.getenv('HPKP_MAX_AGE', '5184000'))  # 60 days
    HPKP_INCLUDE_SUBDOMAINS = True
    HPKP_REPORT_URI = os.getenv('HPKP_REPORT_URI', 'https://bmparliament.ph/api/hpkp-report')

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 864000  # 10 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session alive across browser restarts
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Security - Production configuration with comprehensive origins
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'  # Better compatibility than 'Strict'
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF tokens
CSRF_COOKIE_AGE = 3600  # 1 hour
CSRF_COOKIE_SECURE = True  # Require HTTPS for CSRF cookies
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'  # Custom CSRF failure view

# CSRF_TRUSTED_ORIGINS inherited from base.py with environment-conditional security
# Additional production-specific domains for comprehensive coverage
CSRF_TRUSTED_ORIGINS.extend([
    # Subdomain support for future expansion
    'https://*.bmparliament.ph',
    'https://app.bmparliament.ph',
    'https://api.bmparliament.ph',
    'https://admin.bmparliament.ph',
])

# Add Coolify/Docker deployment domains
COOLIFY_DOMAIN = os.getenv('COOLIFY_DOMAIN')
if COOLIFY_DOMAIN:
    CSRF_TRUSTED_ORIGINS.extend([
        f'https://{COOLIFY_DOMAIN}',
        f'http://{COOLIFY_DOMAIN}',
    ])

# Add any additional CSRF origins from environment
ADDITIONAL_CSRF_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in ADDITIONAL_CSRF_ORIGINS if origin.strip()])

# Remove duplicates and log CSRF trusted origins for debugging
CSRF_TRUSTED_ORIGINS = list(set(CSRF_TRUSTED_ORIGINS))

# Debug logging for CSRF configuration
import logging
logger = logging.getLogger(__name__)
logger.info(f"CSRF_TRUSTED_ORIGINS configured: {CSRF_TRUSTED_ORIGINS}")

# Database settings - Enhanced PostgreSQL configuration for production
import dj_database_url

# Get database URL with fallback
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set in production")

# Parse database configuration with production optimizations
DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,  # Keep connections alive for 10 minutes
        conn_health_checks=True,  # Enable health checks
    )
}

# Enhanced production database configuration
database_config = DATABASES['default']

# Connection pool optimization for production workloads
database_config['OPTIONS'] = {
    # Connection timeouts
    'connect_timeout': 30,  # 30 seconds to establish connection
    'options': '-c statement_timeout=30000',  # 30 second query timeout

    # SSL Configuration for secure connections
    'sslmode': os.getenv('DB_SSL_MODE', 'require'),  # require, prefer, allow, disable
    'sslcert': os.getenv('DB_SSL_CERT', None),
    'sslkey': os.getenv('DB_SSL_KEY', None),
    'sslrootcert': os.getenv('DB_SSL_ROOT_CERT', None),

    # Performance optimizations
    'application_name': f'bmparliament_production_{os.getenv("INSTANCE_ID", "main")}',
    'keepalives_idle': '600',  # Keep alive every 10 minutes
    'keepalives_interval': '30',  # Check every 30 seconds
    'keepalives_count': '3',  # 3 failed checks before considering connection dead
}

# Additional database optimizations
database_config.update({
    # Enable connection pooling with health checks
    'CONN_HEALTH_CHECKS': True,
    'CONN_MAX_AGE': 600,  # 10 minutes
    'ATOMIC_REQUESTS': True,  # Wrap requests in transactions

    # Database engine specific settings
    'ENGINE': 'django.db.backends.postgresql',
    
    # Test database settings for health checks
    'TEST': {
        'NAME': f"{database_config.get('NAME', 'bmparliament')}_test",
        'CHARSET': 'utf8',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    },
})

# Database pool configuration (if using django-db-pool)
ENABLE_DB_POOLING = os.getenv('ENABLE_DB_POOLING', 'False').lower() == 'true'
if ENABLE_DB_POOLING:
    try:
        # Use pgbouncer-style connection pooling if available
        database_config['ENGINE'] = 'django_db_pool.backends.postgresql'
        database_config['POOL_OPTIONS'] = {
            'POOL_SIZE': int(os.getenv('DB_POOL_SIZE', '20')),
            'MAX_OVERFLOW': int(os.getenv('DB_MAX_OVERFLOW', '10')),
            'POOL_TIMEOUT': int(os.getenv('DB_POOL_TIMEOUT', '30')),
            'POOL_RECYCLE': int(os.getenv('DB_POOL_RECYCLE', '3600')),  # 1 hour
            'POOL_PRE_PING': True,  # Validate connections before use
        }
        logger.info("Database connection pooling enabled")
    except ImportError:
        logger.warning("django-db-pool not available, using standard connection management")

# Database health check configuration
DB_HEALTH_CHECK_INTERVAL = int(os.getenv('DB_HEALTH_CHECK_INTERVAL', '30'))  # seconds
DB_HEALTH_CHECK_TIMEOUT = int(os.getenv('DB_HEALTH_CHECK_TIMEOUT', '5'))    # seconds
DB_MAX_RETRIES = int(os.getenv('DB_MAX_RETRIES', '3'))

# Database monitoring and logging
DATABASE_SLOW_QUERY_THRESHOLD = float(os.getenv('DATABASE_SLOW_QUERY_THRESHOLD', '1.0'))  # seconds

# Add database-specific logging
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': os.getenv('DB_LOG_LEVEL', 'WARNING'),
    'propagate': False,
}

# Log slow queries if enabled
if os.getenv('LOG_SLOW_QUERIES', 'False').lower() == 'true':
    LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

logger.info(f"Database configuration completed for: {database_config.get('NAME', 'unknown')}")
logger.info(f"Database connection pool max age: {database_config.get('CONN_MAX_AGE')} seconds")
logger.info(f"Database health checks: {'enabled' if database_config.get('CONN_HEALTH_CHECKS') else 'disabled'}")
logger.info(f"Database SSL mode: {database_config.get('OPTIONS', {}).get('sslmode', 'not specified')}")

# Static files - WhiteNoise for Railway
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise is already configured in base.py MIDDLEWARE

# CDN Configuration
CDN_ENABLED = os.getenv('CDN_ENABLED', 'False').lower() == 'true'
CDN_DOMAIN = os.getenv('CDN_DOMAIN', '')  # e.g., 'cdn.bmparliament.ph' or CloudFront URL

if CDN_ENABLED and CDN_DOMAIN:
    # Use CDN for static files
    STATIC_URL = f'https://{CDN_DOMAIN}/static/'
    
    # Configure WhiteNoise to allow CDN domain
    WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']
    
    # Add CDN headers
    WHITENOISE_ADD_HEADERS_FUNCTION = lambda headers, path, url: dict(headers, **{
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=31536000, immutable',  # 1 year cache
        'X-Content-Type-Options': 'nosniff',
    })
    
    # Media files CDN (if using S3 + CloudFront)
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_CLOUDFRONT_DOMAIN', '')
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Fallback to local serving
    STATIC_URL = '/static/'

# AWS S3 Configuration for media files
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'bmparliament-media')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'ap-southeast-1')

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    # Use S3 for media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # S3 settings
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None  # Use bucket's ACL
    AWS_S3_VERIFY = True
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600  # 1 hour
    
    # Security headers for S3
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day
        'ContentDisposition': 'inline',
    }
    
    # S3 media files location
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/'
    MEDIA_ROOT = ''  # Not used with S3
else:
    # Fallback to local media storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
    # Ensure media files are stored in a persistent volume mounted to /app/media
    # This path aligns with the WORKDIR /app in the Dockerfile and the COPY src /app command.
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    # Ensure the directory exists, though Docker volumes usually handle this.
    os.makedirs(MEDIA_ROOT, exist_ok=True)

# Cache Configuration - Redis
REDIS_URL = os.getenv('REDIS_URL', os.getenv('REDIS_TLS_URL'))

import logging
logger = logging.getLogger(__name__)
logger.info(f"DEBUG: REDIS_URL from environment: {REDIS_URL}")

# Explicitly log Celery broker and result backend URLs
CELERY_BROKER_URL_ENV = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND_ENV = os.getenv('CELERY_RESULT_BACKEND')
logger.info(f"DEBUG: CELERY_BROKER_URL from environment: {CELERY_BROKER_URL_ENV}")
logger.info(f"DEBUG: CELERY_RESULT_BACKEND from environment: {CELERY_RESULT_BACKEND_ENV}")

if REDIS_URL:
    # Parse Redis URL for cache configuration
    import urllib.parse
    redis_parsed = urllib.parse.urlparse(REDIS_URL)
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                    'socket_keepalive': True,
                    'socket_keepalive_options': {},
                },
                'IGNORE_EXCEPTIONS': True,  # Fall back gracefully if Redis is down
                'KEY_PREFIX': 'bmparliament',
                'VERSION': 1,
                'TIMEOUT': 300,  # Default timeout of 5 minutes
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
            }
        },
        # Separate cache for sessions
        'session': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'KEY_PREFIX': 'bmparliament:session',
                'TIMEOUT': 3600,  # 1 hour for sessions
            }
        },
        # Separate cache for rate limiting
        'ratelimit': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'KEY_PREFIX': 'bmparliament:ratelimit',
                'TIMEOUT': 600,  # 10 minutes for rate limit data
            }
        }
    }
    
    # Use Redis for session storage
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'session'
    
    # Configure django-ratelimit to use Redis
    RATELIMIT_USE_CACHE = 'ratelimit'
    RATELIMIT_ENABLE = True
    
else:
    # Fallback to database cache if Redis is not available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache_table',
        }
    }
    
    # Create cache table command: python manage.py createcachetable

# Cache middleware settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'bmparliament'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Sentry Error Tracking Configuration
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Configure Sentry
SENTRY_DSN = os.getenv('SENTRY_DSN')
SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT', 'production')
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1'))
SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '0.1'))

if SENTRY_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            sentry_logging,
        ],
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        release=os.getenv('APP_VERSION', 'unknown'),
        
        # Performance monitoring
        enable_tracing=True,
        
        # Additional options
        before_send=lambda event, hint: filter_sensitive_data(event),
        
        # Ignore certain errors
        ignore_errors=[
            'KeyboardInterrupt',
            'SystemExit',
            'GeneratorExit',
            'Http404',
        ],
    )

def filter_sensitive_data(event):
    """Filter out sensitive data before sending to Sentry."""
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        for header in sensitive_headers:
            if header in event['request']['headers']:
                event['request']['headers'][header] = '[FILTERED]'
    
    # Remove sensitive form data
    if 'request' in event and 'data' in event['request']:
        sensitive_fields = ['password', 'token', 'api_key', 'secret']
        for field in sensitive_fields:
            if field in event['request']['data']:
                event['request']['data'][field] = '[FILTERED]'
    
    return event

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL if REDIS_URL else 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = REDIS_URL if REDIS_URL else 'redis://localhost:6379/0'

# Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Route specific tasks to specific queues
CELERY_TASK_ROUTES = {
    'apps.notifications.tasks.*': {'queue': 'notifications'},
    'apps.analytics.tasks.*': {'queue': 'analytics'},
    'apps.services.tasks.check_application_deadlines': {'queue': 'high_priority'},
}

# Queue configuration
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
    },
    'high_priority': {
        'exchange': 'high_priority',
        'exchange_type': 'direct',
        'routing_key': 'high_priority',
    },
    'notifications': {
        'exchange': 'notifications',
        'exchange_type': 'direct',
        'routing_key': 'notifications',
    },
    'analytics': {
        'exchange': 'analytics',
        'exchange_type': 'direct',
        'routing_key': 'analytics',
    },
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.csrf': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
