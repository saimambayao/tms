"""
Django settings for #BM Parliament project.
"""

import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables

# Track application start time for health check optimization
_APP_START_TIME = time.time()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Correct BASE_DIR for containerized environment
if os.environ.get('DOCKER_CONTAINER'):
    BASE_DIR = Path('/app')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-c3p*g=-@1&=5dq#9m-k=g06^u0x&lc6*aze%5vex)0+m4^g^j&')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_extensions',
    'guardian',
    'crispy_forms', # Add crispy_forms
    'crispy_tailwind', # Add crispy_tailwind
    'widget_tweaks', # Add widget_tweaks
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.constituents',
    'apps.referrals',
    'apps.chapters',
    'apps.services',
    'apps.parliamentary',
    'apps.analytics',
    'apps.communications',
    'apps.documents',
    'apps.notifications',
    'apps.search',
    'apps.dashboards',
    'apps.staff',
    'apps.cooperatives',
    'apps.unified_db',
    # Add other apps as they're created
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # SSL middleware (only active in production)
    'apps.core.middleware.ssl_middleware.SSLRedirectMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # Added for i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Production security middleware - ENABLED
    'apps.users.middleware.SecurityHeadersMiddleware',
    'apps.users.middleware.RateLimitMiddleware',
    'apps.users.middleware.MFAEnforcementMiddleware',
    'apps.users.middleware.SessionSecurityMiddleware',
    # SSL security headers
    'apps.core.middleware.ssl_middleware.SecurityHeadersMiddleware',
    # Performance monitoring - ENABLED
    'apps.core.monitoring.PerformanceMonitoringMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'constituents_extras': 'apps.constituents.templatetags.constituents_extras',
                'unified_db_extras': 'apps.unified_db.templatetags.unified_db_extras',
            },
        },
    },
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Database settings are defined in development.py and production.py

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us' # Default language
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('tl', 'Tagalog/Filipino'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth settings
AUTH_USER_MODEL = 'users.User'  # Custom user model
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'  # Redirect to home after login
LOGOUT_REDIRECT_URL = '/'  # Redirect to home after logout

# Authentication backends (includes Guardian for object-level permissions)
AUTHENTICATION_BACKENDS = (
    'apps.users.admin_bypass_backend.AdminBypassBackend',  # Admin bypass authentication
    'django.contrib.auth.backends.ModelBackend',  # Default Django backend
    'guardian.backends.ObjectPermissionBackend',   # Guardian object permissions
)

# Security settings
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF Configuration - Secure environment-conditional setup
CSRF_TRUSTED_ORIGINS = []

# Production domains (always included - secure HTTPS only)
PRODUCTION_DOMAINS = [
    'https://bmparliament.ph',
    'https://www.bmparliament.ph',
]
CSRF_TRUSTED_ORIGINS.extend(PRODUCTION_DOMAINS)

# Environment-specific additions
if DEBUG:  # Development/testing only
    DEVELOPMENT_DOMAINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://bmparliament.ph',      # For local testing with production domain
        'http://www.bmparliament.ph'   # For local testing with production domain
    ]
    CSRF_TRUSTED_ORIGINS.extend(DEVELOPMENT_DOMAINS)

# Railway domains (validated for security)
RAILWAY_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_DOMAIN and RAILWAY_DOMAIN.endswith('.railway.app'):
    CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_DOMAIN}')
    if DEBUG:  # Allow HTTP in development only
        CSRF_TRUSTED_ORIGINS.append(f'http://{RAILWAY_DOMAIN}')

# Allow environment override (with validation)
CUSTOM_CSRF_ORIGINS = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if CUSTOM_CSRF_ORIGINS:
    custom_origins = [origin.strip() for origin in CUSTOM_CSRF_ORIGINS.split(',') if origin.strip()]
    # In production, only allow HTTPS origins from environment override
    if not DEBUG:
        custom_origins = [origin for origin in custom_origins if origin.startswith('https://')]
    CSRF_TRUSTED_ORIGINS.extend(custom_origins)

# Remove duplicates while preserving order
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

# CSRF Cookie Configuration
CSRF_COOKIE_SAMESITE = 'Lax'  # Better compatibility than 'Strict'
CSRF_COOKIE_AGE = 3600  # 1 hour
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF tokens

# Session settings
SESSION_TIMEOUT_MINUTES = 14400  # 10 days in minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session alive across browser restarts
SESSION_COOKIE_AGE = 864000  # 10 days in seconds

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes
MAX_API_REQUESTS_PER_MINUTE = 100

# Password validation
AUTH_PASSWORD_VALIDATORS.extend([
    {
        'NAME': 'apps.users.security.PasswordStrengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
])

# Feature flags for Production version
FEATURES = {
    'ministry_programs': True,    # Production: enabled - full programs catalog and management
    'referral_system': False,     # Production: DISABLED - awaiting MOAs and government readiness
    'chapters': True,             # Production: enabled - chapter information and management
    'announcements': True,        # Production: enabled - announcements system
    'constituent_management': True, # Production: enabled - basic member management
    'staff_directory': True,      # Production: enabled - staff profiles and directory
}

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Enhanced Production Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{{ "level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}" }}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'application_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'application.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 20,
            'formatter': 'json',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'performance.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'application_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['application_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.users.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.referrals': {
            'handlers': ['application_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.performance': {
            'handlers': ['performance_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'root': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
        },
    },
}

# Cache configuration
if os.environ.get('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PASSWORD': os.environ.get('REDIS_PASSWORD', ''),
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Email configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@bmparliament.ph')

# Celery configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

# Sentry Error Tracking and Performance Monitoring
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.environ.get('SENTRY_ENVIRONMENT', 'development'),
        integrations=[
            DjangoIntegration(),
            sentry_logging,
            RedisIntegration(),
        ],
        # Performance Monitoring
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        # Send personal data (emails, usernames, etc.)
        send_default_pii=False,
        # Release tracking
        release=os.environ.get('GIT_COMMIT_SHA', 'development'),
        # Custom tags
        before_send=lambda event, hint: event if not DEBUG else None,  # Don't send in debug mode
    )

# Application Performance Monitoring
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# Monitoring and alerting configuration
ENABLE_PERFORMANCE_MONITORING = os.environ.get('ENABLE_PERFORMANCE_MONITORING', 'True').lower() == 'true'
PERFORMANCE_THRESHOLD_MS = int(os.environ.get('PERFORMANCE_THRESHOLD_MS', '1000'))  # 1 second

# Health check configuration
HEALTH_CHECK_TOKEN = os.environ.get('HEALTH_CHECK_TOKEN', '')
HEALTH_CHECK_ALLOWED_IPS = os.environ.get('HEALTH_CHECK_ALLOWED_IPS', '').split(',') if os.environ.get('HEALTH_CHECK_ALLOWED_IPS') else []

# SMS Settings (Government-funded OTP service for constituent accessibility)
# The government covers all SMS costs to ensure equal access to security features
SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'console')  # Options: 'console', 'semaphore', 'twilio'

# Semaphore SMS (Recommended Philippine SMS Gateway)
# Government contract rates: ~₱0.15-0.30 per SMS with bulk discounts
SEMAPHORE_API_KEY = os.environ.get('SEMAPHORE_API_KEY', '')
SEMAPHORE_SENDER_NAME = os.environ.get('SEMAPHORE_SENDER_NAME', 'BMPARLIAMENT')

# Twilio SMS (International backup option)
# Higher rates but reliable: ~₱1.50-2.00 per SMS to PH numbers
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

# SMS OTP Configuration
SMS_OTP_LENGTH = 6
SMS_OTP_VALIDITY_MINUTES = 5
SMS_OTP_MAX_REQUESTS_PER_HOUR = 3  # Rate limiting to control costs
