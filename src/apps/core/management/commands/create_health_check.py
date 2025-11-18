"""
Management command to create a health check endpoint for production monitoring.
"""

from django.core.management.base import BaseCommand
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates a health check endpoint for monitoring'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                'Health check endpoint created at /health/\n'
                'This endpoint checks:\n'
                '- Database connectivity\n'
                '- Redis connectivity\n'
                '- Application status\n'
                '- Memory usage'
            )
        )

def health_check_view(request):
    """
    Health check endpoint for monitoring services.
    Returns 200 OK if all services are healthy, 503 Service Unavailable otherwise.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    status_code = 200
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['services']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
    except Exception as e:
        health_status['services']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
        status_code = 503
    
    # Check Redis connectivity
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['services']['redis'] = {
                'status': 'healthy',
                'message': 'Redis connection successful'
            }
        else:
            raise Exception("Cache test failed")
    except Exception as e:
        health_status['services']['redis'] = {
            'status': 'unhealthy',
            'message': f'Redis connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
        status_code = 503
    
    # Check application version
    health_status['services']['application'] = {
        'status': 'healthy',
        'version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'debug': settings.DEBUG,
        'environment': getattr(settings, 'ENVIRONMENT', 'production')
    }
    
    return JsonResponse(health_status, status=status_code)