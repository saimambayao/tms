"""
Performance monitoring and alerting for #FahanieCares platform.
"""

import time
import logging
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse

logger = logging.getLogger('apps.core.performance')

class PerformanceMonitoringMiddleware:
    """
    Middleware to monitor application performance and log slow requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.threshold_ms = getattr(settings, 'PERFORMANCE_THRESHOLD_MS', 1000)
        self.monitoring_enabled = getattr(settings, 'ENABLE_PERFORMANCE_MONITORING', True)
    
    def __call__(self, request):
        if not self.monitoring_enabled:
            return self.get_response(request)
        
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate response time
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Log performance metrics
        self._log_performance_metrics(request, response, response_time_ms)
        
        # Add performance headers for monitoring
        response['X-Response-Time'] = f"{response_time_ms:.2f}ms"
        
        return response
    
    def _log_performance_metrics(self, request, response, response_time_ms):
        """Log performance metrics for monitoring."""
        
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'response_time_ms': round(response_time_ms, 2),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'remote_addr': self._get_client_ip(request),
        }
        
        # Log slow requests as warnings
        if response_time_ms > self.threshold_ms:
            logger.warning(
                f"Slow request detected: {request.method} {request.path} "
                f"took {response_time_ms:.2f}ms (threshold: {self.threshold_ms}ms)",
                extra=log_data
            )
        else:
            # Log normal requests as info
            logger.info(
                f"Request processed: {request.method} {request.path} "
                f"in {response_time_ms:.2f}ms",
                extra=log_data
            )
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AlertingService:
    """
    Service for sending alerts when critical issues are detected.
    """
    
    @staticmethod
    def send_performance_alert(request_path, response_time_ms, threshold_ms):
        """Send alert for performance issues."""
        logger.error(
            f"ALERT: Critical performance issue detected on {request_path}. "
            f"Response time: {response_time_ms}ms (threshold: {threshold_ms}ms)"
        )
        
        # In production, this could send emails, Slack notifications, etc.
        # For now, we log the alert
    
    @staticmethod
    def send_error_alert(error_message, request_path=None, user_id=None):
        """Send alert for application errors."""
        alert_data = {
            'timestamp': timezone.now().isoformat(),
            'error_message': error_message,
            'request_path': request_path,
            'user_id': user_id,
        }
        
        logger.error(
            f"ALERT: Application error detected: {error_message}",
            extra=alert_data
        )
    
    @staticmethod
    def send_security_alert(event_type, request_ip, details=None):
        """Send alert for security events."""
        security_logger = logging.getLogger('apps.users.security')
        
        alert_data = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'request_ip': request_ip,
            'details': details,
        }
        
        security_logger.warning(
            f"SECURITY ALERT: {event_type} from IP {request_ip}",
            extra=alert_data
        )


def performance_report():
    """
    Generate performance report for the last 24 hours.
    This function can be called periodically to generate reports.
    """
    try:
        from django.db import connection
        
        # Get database query count and time
        queries_count = len(connection.queries) if settings.DEBUG else 'N/A'
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'database_queries': queries_count,
            'features_enabled': sum(1 for v in settings.FEATURES.values() if v),
            'monitoring_enabled': getattr(settings, 'ENABLE_PERFORMANCE_MONITORING', True),
            'performance_threshold_ms': getattr(settings, 'PERFORMANCE_THRESHOLD_MS', 1000),
        }
        
        logger.info("Performance report generated", extra=report)
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate performance report: {str(e)}")
        return None


def health_status_check(detailed=False):
    """
    Enhanced comprehensive health status check for monitoring systems.
    
    Args:
        detailed (bool): Whether to include detailed diagnostics
    
    Returns:
        dict: Health status with detailed information
    """
    import os
    from django.db import connection
    from django.db.utils import OperationalError, DatabaseError
    from django.core.cache import cache
    
    status = {
        'timestamp': timezone.now().isoformat(),
        'status': 'healthy',
        'checks': {},
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'version': getattr(settings, 'APP_VERSION', '1.0.0')
    }
    
    # Enhanced Database check with retry logic
    db_start_time = time.time()
    max_retries = 3
    db_healthy = False
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Health monitoring: Database connectivity attempt {attempt + 1}/{max_retries}")
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1, current_database(), version()")
                result = cursor.fetchone()
                
                if result and result[0] == 1:
                    db_duration = round((time.time() - db_start_time) * 1000, 2)
                    status['checks']['database'] = {
                        'status': 'healthy',
                        'response_time_ms': db_duration,
                        'attempts': attempt + 1,
                        'database_name': result[1] if detailed else '[HIDDEN]',
                        'postgres_version': result[2].split(' ')[0] if detailed and result[2] else None,
                        'connection_info': {
                            'host': connection.settings_dict.get('HOST', 'localhost') if detailed else '[HIDDEN]',
                            'port': connection.settings_dict.get('PORT', '5432'),
                            'ssl_mode': connection.settings_dict.get('OPTIONS', {}).get('sslmode', 'not specified') if detailed else '[HIDDEN]'
                        } if detailed else {}
                    }
                    logger.info(f"Health monitoring: Database healthy in {db_duration}ms on attempt {attempt + 1}")
                    db_healthy = True
                    break
                else:
                    raise Exception('Database query returned unexpected result')
                    
        except (OperationalError, DatabaseError) as e:
            error_msg = str(e)
            logger.warning(f"Health monitoring: Database attempt {attempt + 1} failed: {error_msg}")
            
            # Enhanced error classification
            error_type = 'unknown'
            if 'connection' in error_msg.lower():
                error_type = 'connection_failed'
            elif 'timeout' in error_msg.lower():
                error_type = 'timeout'
            elif 'authentication' in error_msg.lower():
                error_type = 'auth_failed'
            elif 'permission' in error_msg.lower():
                error_type = 'permission_denied'
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                status['checks']['database'] = {
                    'status': 'unhealthy',
                    'error': error_msg,
                    'error_type': error_type,
                    'attempts': max_retries,
                    'response_time_ms': round((time.time() - db_start_time) * 1000, 2),
                    'troubleshooting': _get_database_troubleshooting_info(error_type) if detailed else None
                }
                status['status'] = 'unhealthy'
                
        except Exception as e:
            error_msg = f'Unexpected database error: {str(e)}'
            logger.error(f"Health monitoring: {error_msg}")
            status['checks']['database'] = {
                'status': 'unhealthy',
                'error': error_msg,
                'error_type': 'unexpected',
                'attempts': attempt + 1,
                'response_time_ms': round((time.time() - db_start_time) * 1000, 2)
            }
            status['status'] = 'unhealthy'
            break
    
    # Enhanced Cache check with multiple backends
    cache_start_time = time.time()
    cache_backends = ['default']
    if hasattr(settings, 'CACHES') and 'session' in settings.CACHES:
        cache_backends.append('session')
    
    for backend in cache_backends:
        try:
            test_key = f'health_check_{backend}_{int(time.time())}'
            test_value = f'test_value_{backend}'
            
            cache_instance = cache if backend == 'default' else cache.caches[backend]
            cache_instance.set(test_key, test_value, 60)
            cache_value = cache_instance.get(test_key)
            
            if cache_value == test_value:
                cache_duration = round((time.time() - cache_start_time) * 1000, 2)
                status['checks'][f'cache_{backend}'] = {
                    'status': 'healthy',
                    'response_time_ms': cache_duration,
                    'backend': backend
                }
                cache_instance.delete(test_key)  # Clean up
                logger.info(f"Health monitoring: Cache {backend} healthy in {cache_duration}ms")
            else:
                raise Exception(f'Cache {backend} not responding correctly')
                
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Health monitoring: Cache {backend} failed: {error_msg}")
            status['checks'][f'cache_{backend}'] = {
                'status': 'unhealthy',
                'error': error_msg,
                'backend': backend,
                'response_time_ms': round((time.time() - cache_start_time) * 1000, 2)
            }
            if status['status'] == 'healthy':
                status['status'] = 'degraded'
    
    # Enhanced Environment validation
    critical_env_vars = ['DATABASE_URL', 'DJANGO_SECRET_KEY']
    optional_env_vars = ['REDIS_URL', 'SENTRY_DSN', 'EMAIL_HOST']
    
    missing_critical = [var for var in critical_env_vars if not os.environ.get(var)]
    missing_optional = [var for var in optional_env_vars if not os.environ.get(var)]
    
    status['checks']['environment'] = {
        'status': 'unhealthy' if missing_critical else 'healthy',
        'critical_vars_missing': missing_critical,
        'optional_vars_missing': missing_optional if detailed else len(missing_optional),
        'environment_name': getattr(settings, 'ENVIRONMENT', 'development')
    }
    
    if missing_critical:
        status['status'] = 'unhealthy'
        logger.error(f"Health monitoring: Critical environment variables missing: {missing_critical}")
    elif missing_optional:
        logger.warning(f"Health monitoring: Optional environment variables missing: {missing_optional}")
    
    # Enhanced Features check
    try:
        features = getattr(settings, 'FEATURES', {})
        enabled_features = sum(1 for v in features.values() if v)
        total_features = len(features)
        
        status['checks']['features'] = {
            'status': 'healthy',
            'enabled': enabled_features,
            'total': total_features,
            'feature_coverage': f"{enabled_features}/{total_features}",
            'details': features if detailed else None
        }
    except Exception as e:
        status['checks']['features'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        status['status'] = 'degraded'
    
    # System resource checks (if detailed)
    if detailed:
        try:
            import psutil
            status['checks']['system_resources'] = {
                'status': 'healthy',
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except ImportError:
            status['checks']['system_resources'] = {
                'status': 'unavailable',
                'error': 'psutil not installed'
            }
        except Exception as e:
            status['checks']['system_resources'] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Overall status determination
    if any(check.get('status') == 'unhealthy' for check in status['checks'].values()):
        status['status'] = 'unhealthy'
    elif any(check.get('status') == 'degraded' for check in status['checks'].values()):
        if status['status'] != 'unhealthy':
            status['status'] = 'degraded'
    
    # Log health check result
    if status['status'] == 'unhealthy':
        logger.error(f"Health monitoring: System unhealthy - {status}")
    elif status['status'] == 'degraded':
        logger.warning(f"Health monitoring: System degraded - {status}")
    else:
        logger.info(f"Health monitoring: System healthy")
    
    return status


def _get_database_troubleshooting_info(error_type):
    """
    Get troubleshooting information for database errors.
    
    Args:
        error_type (str): Type of database error
        
    Returns:
        dict: Troubleshooting information
    """
    troubleshooting = {
        'connection_failed': {
            'possible_causes': [
                'Database server is down',
                'Network connectivity issues',
                'Incorrect host/port configuration',
                'Firewall blocking connections'
            ],
            'solutions': [
                'Check DATABASE_URL environment variable',
                'Verify database server status',
                'Test network connectivity',
                'Check firewall settings'
            ]
        },
        'timeout': {
            'possible_causes': [
                'Database server overloaded',
                'Slow query execution',
                'Network latency issues',
                'Connection pool exhaustion'
            ],
            'solutions': [
                'Increase connection timeout settings',
                'Optimize database queries',
                'Scale database resources',
                'Review connection pool configuration'
            ]
        },
        'auth_failed': {
            'possible_causes': [
                'Incorrect username/password',
                'User permissions insufficient',
                'Authentication method mismatch'
            ],
            'solutions': [
                'Verify DATABASE_URL credentials',
                'Check user permissions in database',
                'Review authentication configuration'
            ]
        },
        'permission_denied': {
            'possible_causes': [
                'Database user lacks required permissions',
                'Database access restrictions',
                'SSL certificate issues'
            ],
            'solutions': [
                'Grant necessary permissions to database user',
                'Review database access policies',
                'Check SSL configuration'
            ]
        }
    }
    
    return troubleshooting.get(error_type, {
        'message': 'Unknown error type - check logs for more details'
    })