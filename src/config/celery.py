"""
Celery configuration for #FahanieCares project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('fahanie_cares')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    
    # Generate daily reports at 2 AM
    'generate-daily-reports': {
        'task': 'apps.analytics.tasks.generate_daily_reports',
        'schedule': crontab(hour=2, minute=0),
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },
    
    # Clean up old sessions daily at 3 AM
    'cleanup-sessions': {
        'task': 'apps.users.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=3, minute=0),
        'options': {
            'expires': 3600,
        }
    },
    
    # Send notification digest every morning at 8 AM
    'send-notification-digest': {
        'task': 'apps.notifications.tasks.send_daily_digest',
        'schedule': crontab(hour=8, minute=0),
        'options': {
            'expires': 3600,
        }
    },
    
    # Check service application deadlines daily
    'check-application-deadlines': {
        'task': 'apps.services.tasks.check_application_deadlines',
        'schedule': crontab(hour=9, minute=0),
        'options': {
            'expires': 3600,
        }
    },
    
    # Update cache warming every hour
    'warm-cache': {
        'task': 'apps.core.tasks.warm_cache',
        'schedule': crontab(minute=0),  # Every hour
        'options': {
            'expires': 3600,
        }
    },
    
    # Database maintenance weekly on Sunday at 4 AM
    'database-maintenance': {
        'task': 'apps.core.tasks.database_maintenance',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
        'options': {
            'expires': 7200,  # Expire after 2 hours
        }
    },
}

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    result_compression='gzip',
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
)

@app.task(bind=True, name='debug_task')
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')