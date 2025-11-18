"""
Background tasks for core app using Celery.
"""

from celery import shared_task
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.core.tasks.warm_cache')
def warm_cache():
    """
    Pre-warm cache with frequently accessed data.
    Runs hourly to ensure fast response times.
    """
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        warmed_urls = []
        
        # List of URLs to warm
        urls_to_warm = [
            '/',
            '/programs/',
            '/ministries-ppas/',
            '/chapters/',
            '/about/',
            '/contact/',
        ]
        
        for url in urls_to_warm:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    warmed_urls.append(url)
                    logger.info(f"Warmed cache for: {url}")
                else:
                    logger.warning(f"Failed to warm cache for {url}: status {response.status_code}")
            except Exception as e:
                logger.error(f"Error warming cache for {url}: {str(e)}")
        
        return {
            'status': 'success',
            'warmed_urls': warmed_urls,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache warming failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }

@shared_task(name='apps.core.tasks.database_maintenance')
def database_maintenance():
    """
    Perform weekly database maintenance tasks.
    Runs every Sunday at 4 AM.
    """
    try:
        maintenance_tasks = []
        
        with connection.cursor() as cursor:
            # Analyze tables for query optimization
            cursor.execute("ANALYZE;")
            maintenance_tasks.append("Analyzed all tables")
            
            # Clean up old sessions
            from django.contrib.sessions.models import Session
            expired_sessions = Session.objects.filter(
                expire_date__lt=timezone.now()
            ).delete()
            maintenance_tasks.append(f"Deleted {expired_sessions[0]} expired sessions")
            
            # Clean up old log entries (keep last 90 days)
            from django.contrib.admin.models import LogEntry
            cutoff_date = timezone.now() - timezone.timedelta(days=90)
            old_logs = LogEntry.objects.filter(
                action_time__lt=cutoff_date
            ).delete()
            maintenance_tasks.append(f"Deleted {old_logs[0]} old log entries")
        
        # Clear old cache entries
        cache.clear()
        maintenance_tasks.append("Cleared cache")
        
        logger.info(f"Database maintenance completed: {', '.join(maintenance_tasks)}")
        
        return {
            'status': 'success',
            'tasks_completed': maintenance_tasks,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database maintenance failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }

@shared_task(name='apps.core.tasks.health_check_notification')
def health_check_notification():
    """
    Send notification if health checks are failing.
    """
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Check health endpoint
        response = client.get('/health/')
        
        if response.status_code != 200:
            # Send alert (implement notification logic)
            logger.error(f"Health check failed with status: {response.status_code}")
            
            # In production, this would send to Slack, email, etc.
            return {
                'status': 'alert_sent',
                'health_status': response.status_code,
                'timestamp': timezone.now().isoformat()
            }
        
        return {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check notification failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }