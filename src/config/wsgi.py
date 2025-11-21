"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Auto-detect environment and use appropriate settings
if os.environ.get('ENVIRONMENT') == 'production' or os.environ.get('DATABASE_URL'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
elif os.environ.get('ENVIRONMENT') == 'development' or os.environ.get('DEBUG') == 'True':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
else:
    # Fallback to base settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

application = get_wsgi_application()
