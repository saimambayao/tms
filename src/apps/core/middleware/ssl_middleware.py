"""
SSL and Security Middleware for #BM Parliament

This middleware handles SSL redirection, security headers,
and certificate validation at the Django application level.
"""

import logging
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SSLRedirectMiddleware(MiddlewareMixin):
    """
    Middleware to redirect HTTP requests to HTTPS.
    Only active in production when SECURE_SSL_REDIRECT is True.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Only enable in production
        if not settings.SECURE_SSL_REDIRECT:
            raise MiddlewareNotUsed("SSL redirect is disabled")
        
        # Exempt paths that should not be redirected
        self.exempt_paths = [
            '/.well-known/acme-challenge/',  # Let's Encrypt verification
            '/health/',  # Health check endpoint
            '/robots.txt',
        ]
    
    def process_request(self, request):
        """Process incoming request and redirect to HTTPS if needed."""
        # Check if request is already HTTPS
        if request.is_secure():
            return None
        
        # Check for exempted paths
        for path in self.exempt_paths:
            if request.path.startswith(path):
                return None
        
        # Check for development/internal IPs
        if hasattr(settings, 'INTERNAL_IPS') and request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return None
        
        # Build HTTPS URL
        url = request.build_absolute_uri()
        https_url = url.replace('http://', 'https://', 1)
        
        logger.info(f"Redirecting HTTP to HTTPS: {url} -> {https_url}")
        
        # Return permanent redirect
        return HttpResponsePermanentRedirect(https_url)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    Complements Django's built-in security middleware.
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Content Security Policy
        if not response.has_header('Content-Security-Policy'):
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://static.cloudflareinsights.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
                "font-src 'self' https://fonts.gstatic.com data:",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' https://api.notion.com wss: https://cloudflareinsights.com",
                "frame-src 'self' https://www.google.com https://maps.google.com https://*.google.com",
                "frame-ancestors 'none'",
                "form-action 'self'",
                "base-uri 'self'",
                "object-src 'none'",
            ]
            response['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # Feature Policy / Permissions Policy
        if not response.has_header('Permissions-Policy'):
            permissions = [
                "geolocation=()",
                "microphone=()",
                "camera=()",
                "payment=()",
                "usb=()",
                "accelerometer=()",
                "gyroscope=()",
                "magnetometer=()",
            ]
            response['Permissions-Policy'] = ", ".join(permissions)
        
        # Referrer Policy
        if not response.has_header('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # X-Content-Type-Options
        if not response.has_header('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options (if not set by Django)
        if not response.has_header('X-Frame-Options'):
            response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection (for older browsers)
        if not response.has_header('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # Remove server header
        if 'Server' in response:
            del response['Server']
        
        # Add custom security header
        response['X-Security-Policy'] = 'BM Parliament Security Policy v1.0'
        
        return response


class CertificatePinningMiddleware(MiddlewareMixin):
    """
    Middleware for HTTP Public Key Pinning (HPKP).
    Use with caution - incorrect configuration can make site inaccessible.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Only enable if explicitly configured
        if not getattr(settings, 'ENABLE_CERTIFICATE_PINNING', False):
            raise MiddlewareNotUsed("Certificate pinning is disabled")
        
        # Get pin configurations
        self.pin_sha256_list = getattr(settings, 'CERTIFICATE_PINS', [])
        self.max_age = getattr(settings, 'HPKP_MAX_AGE', 5184000)  # 60 days default
        self.include_subdomains = getattr(settings, 'HPKP_INCLUDE_SUBDOMAINS', True)
        self.report_uri = getattr(settings, 'HPKP_REPORT_URI', None)
    
    def process_response(self, request, response):
        """Add HPKP header to response."""
        if not request.is_secure():
            return response
        
        if not self.pin_sha256_list:
            logger.warning("Certificate pinning enabled but no pins configured")
            return response
        
        # Build HPKP header
        pins = [f'pin-sha256="{pin}"' for pin in self.pin_sha256_list]
        hpkp_header = f"{'; '.join(pins)}; max-age={self.max_age}"
        
        if self.include_subdomains:
            hpkp_header += "; includeSubDomains"
        
        if self.report_uri:
            hpkp_header += f'; report-uri="{self.report_uri}"'
        
        response['Public-Key-Pins'] = hpkp_header
        
        return response


class SSLCertificateValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate SSL certificate information.
    Logs certificate details for monitoring.
    """
    
    def process_request(self, request):
        """Log SSL certificate information if available."""
        if not request.is_secure():
            return None
        
        # Get SSL information from request
        ssl_info = {}
        
        # Client certificate (if mutual TLS is enabled)
        if 'SSL_CLIENT_CERT' in request.META:
            ssl_info['client_cert'] = request.META['SSL_CLIENT_CERT']
            ssl_info['client_verify'] = request.META.get('SSL_CLIENT_VERIFY', 'NONE')
        
        # Server certificate info
        ssl_info['protocol'] = request.META.get('SSL_PROTOCOL', 'Unknown')
        ssl_info['cipher'] = request.META.get('SSL_CIPHER', 'Unknown')
        
        # Log SSL information
        if ssl_info:
            logger.debug(f"SSL connection info: {ssl_info}")
        
        return None
