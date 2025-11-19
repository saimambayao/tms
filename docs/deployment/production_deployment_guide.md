# BM Parliament Production Deployment Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Claude Code Development Strategy](#claude-code-development-strategy)
4. [Critical Path Implementation](#critical-path-implementation)
5. [Parallel Development Streams](#parallel-development-streams)
6. [Quality Assurance Framework](#quality-assurance-framework)
7. [Security & Compliance](#security--compliance)
8. [Deployment Automation](#deployment-automation)
9. [Monitoring & Operations](#monitoring--operations)
10. [Go-Live Procedures](#go-live-procedures)
11. [Post-Launch Operations](#post-launch-operations)
12. [Troubleshooting & Support](#troubleshooting--support)

---

## Executive Summary

This guide outlines the systematic approach to deploying the BM Parliament platform to production, leveraging Claude Code's autonomous development capabilities for rapid, high-quality delivery. The strategy emphasizes **parallel execution**, **continuous quality assurance**, and **security-first development**.

### Key Objectives
- **Zero-downtime production deployment** with automated rollback capabilities
- **Comprehensive security hardening** meeting government security standards
- **Performance optimization** for high-availability public service delivery
- **Autonomous development workflow** using Claude Code's super-agentic capabilities
- **Complete monitoring and alerting** for proactive issue resolution

### Success Criteria
- ✅ All security audits passed with zero critical vulnerabilities
- ✅ Performance benchmarks met under production load
- ✅ 99.9% uptime SLA achievable with current infrastructure
- ✅ Complete feature set enabled and tested
- ✅ Automated deployment pipeline functional

---

## Current State Analysis

### Strengths Already in Place
Based on codebase analysis and existing `PRODUCTION_READINESS_REPORT.md`:

✅ **Security Foundation**
- Django security middleware configured (`config/settings/production.py`)
- HTTPS enforcement with HSTS enabled
- CSRF and XSS protection implemented
- Role-based access control (RBAC) with Guardian

✅ **Infrastructure Ready**
- Docker containerization with PostgreSQL, Redis, Nginx
- Production settings configuration with environment variables
- WhiteNoise static file serving
- Database optimization and connection pooling

✅ **Application Architecture**
- Modular Django app structure following best practices
- Component-based frontend with reusable elements
- PostgreSQL-native data management for maximum performance
- Comprehensive logging configuration

✅ **Member Registration System**
- Production-ready with comprehensive testing (per existing report)
- Province/municipality dropdown system functional
- Form validation and security measures implemented

### Critical Gaps Requiring Immediate Attention

⚠️ **Security Middleware Disabled**
```python
# config/settings/base.py:70-73 (Currently commented out)
# 'apps.users.middleware.SecurityHeadersMiddleware',
# 'apps.users.middleware.RateLimitMiddleware', 
# 'apps.users.middleware.MFAMiddleware',
# 'apps.users.middleware.SessionSecurityMiddleware',
```

⚠️ **Core Features Disabled in Alpha**
```python
# config/settings/base.py:201-208
FEATURES = {
    'ministry_programs': False,   # Critical for service delivery
    'referral_system': False,     # Core platform functionality
    # ... other features
}
```

⚠️ **Missing Production Infrastructure**
- No CI/CD pipeline for automated deployment
- No error monitoring or application performance monitoring
- No automated backup and recovery procedures
- No load testing or performance validation

---

## Claude Code Development Strategy

### Autonomous Development Principles

This deployment follows the **ULTRATHINK → PLAN → READ → THINK → CODE → TEST → VERIFY** workflow outlined in `CLAUDE.md`.

#### MCP Tool Integration
```bash
# Systematic tool usage throughout development
TodoWrite/TodoRead    # Continuous task tracking and progress visibility
Context7             # Research best practices, frameworks, security standards  
Taskmaster-AI        # Project management, dependency tracking, task breakdown
Memory               # Build knowledge base of decisions, patterns, learnings
Sequential Thinking  # Complex multi-step problem solving
```

#### Quality Gates (Enforced at Every Step)
- [ ] **All tests pass** - Unit, integration, end-to-end
- [ ] **Security scans pass** - No critical vulnerabilities 
- [ ] **Performance benchmarks met** - Response time and resource usage within limits
- [ ] **Documentation updated** - Code changes include documentation updates
- [ ] **Manual verification** - Critical path functionality manually tested

#### Parallel Execution Strategy
```
Critical Path (Sequential):     Parallel Streams (Concurrent):
├── Security Hardening         ├── Infrastructure Automation
├── Feature Enablement         ├── Quality Assurance Expansion  
└── Monitoring Setup          ├── Documentation & Compliance
                              └── Performance & Scalability
```

---

## Critical Path Implementation

These tasks must be completed sequentially due to dependencies:

### CP-1: Security Hardening and Environment Setup

#### Objective
Enable all security measures and create production-ready environment configuration.

#### Implementation Tasks

**1. Enable Security Middleware**
```python
# File: config/settings/base.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.AlphaFeatureMiddleware',
    # Enable production security middleware
    'apps.users.middleware.SecurityHeadersMiddleware',
    'apps.users.middleware.RateLimitMiddleware',
    'apps.users.middleware.MFAMiddleware', 
    'apps.users.middleware.SessionSecurityMiddleware',
]
```

**2. Production Environment Configuration**
```bash
# File: .env.production (template)
# CRITICAL: Django Settings Module (MUST BE FIRST)
DJANGO_SETTINGS_MODULE=config.settings.production

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname
DB_NAME=bmparliament_production
DB_USER=bmparliament_user
DB_PASSWORD=[SECURE_PASSWORD]
DB_HOST=production-db-host
DB_PORT=5432

# Security Configuration  
DJANGO_SECRET_KEY=[SECURE_SECRET_KEY_32_CHARS_MIN]
ALLOWED_HOSTS=bm-parliament.gov.ph,www.bm-parliament.gov.ph
CSRF_TRUSTED_ORIGINS=https://bm-parliament.gov.ph,https://www.bm-parliament.gov.ph
DEBUG=False

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=[EMAIL_USER]
EMAIL_HOST_PASSWORD=[EMAIL_PASSWORD]
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@bm-parliament.gov.ph

# Cache Configuration
REDIS_URL=redis://redis-host:6379/0
REDIS_PASSWORD=[REDIS_PASSWORD]

# External API Configuration
NOTION_TOKEN=[NOTION_INTEGRATION_TOKEN]
NOTION_DATABASE_ID=[NOTION_DATABASE_ID]

# AWS Configuration (if using)
AWS_ACCESS_KEY_ID=[AWS_KEY]
AWS_SECRET_ACCESS_KEY=[AWS_SECRET]
AWS_STORAGE_BUCKET_NAME=[BUCKET_NAME]

# Monitoring
SENTRY_DSN=[SENTRY_DSN]
```

**3. SSL and Domain Configuration**
```nginx
# File: deployment/nginx.conf (production)
server {
    listen 80;
    server_name bm-parliament.gov.ph www.bm-parliament.gov.ph;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bm-parliament.gov.ph www.bm-parliament.gov.ph;
    
    ssl_certificate /etc/letsencrypt/live/bm-parliament.gov.ph/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bm-parliament.gov.ph/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    location / {
        proxy_pass http://web:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Quality Gate**: Security audit passes with zero critical vulnerabilities

### CP-2: Feature Enablement and Testing

#### Objective
Enable all core features disabled in alpha version and ensure comprehensive testing.

#### Implementation Tasks

**1. Enable Core Features**
```python
# File: config/settings/base.py
FEATURES = {
    'ministry_programs': True,    # Enable full programs catalog and management
    'referral_system': False,     # DISABLED - Awaiting government MOAs and readiness  
    'chapters': True,             # Already enabled - chapter information and management
    'announcements': True,        # Already enabled - announcements system
    'constituent_management': True, # Already enabled - basic member management
    'staff_directory': True,      # Already enabled - staff profiles and directory
}
```

**⚠️ IMPORTANT POLICY NOTE:**
The **referral system has been disabled** pending completion of Memorandums of Agreement (MOAs) with government agencies. This is a policy decision, not a technical limitation. The feature can be re-enabled via feature flags once legal frameworks are in place.

**2. Feature Testing Suite**
```python
# File: tests/test_production_features.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class ProductionFeatureTests(TestCase):
    """Test all enabled features work correctly in production mode."""
    
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_ministry_programs_enabled(self):
        """Test ministry programs feature is functional."""
        response = self.client.get(reverse('ministry_programs'))
        self.assertEqual(response.status_code, 200)
    
    def test_referral_system_enabled(self):
        """Test referral system is functional."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('referral_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_feature_security_controls(self):
        """Test feature-level security controls work."""
        # Test unauthorized access is properly blocked
        response = self.client.get(reverse('staff_dashboard'))
        self.assertIn(response.status_code, [302, 403])  # Redirect to login or forbidden
```

**3. End-to-End Workflow Testing**
```python
# File: tests/test_e2e_workflows.py
from django.test import TestCase, Client
from django.urls import reverse

class EndToEndWorkflowTests(TestCase):
    """Test complete user workflows function correctly."""
    
    def test_constituent_registration_to_service_request(self):
        """Test complete workflow from registration to service request."""
        # 1. User registers as constituent
        response = self.client.post(reverse('member_registration'), {
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'email': 'juan@example.com',
            # ... complete form data
        })
        self.assertEqual(response.status_code, 302)  # Redirect to success
        
        # 2. User logs in
        self.client.login(username='juan@example.com', password='password123')
        
        # 3. User creates service request
        response = self.client.post(reverse('referral_create'), {
            'service_type': 'health',
            'description': 'Medical assistance needed',
            # ... complete referral data
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. Verify referral was created and is trackable
        response = self.client.get(reverse('referral_list'))
        self.assertContains(response, 'Medical assistance needed')
```

**Quality Gate**: All enabled features pass end-to-end testing

### CP-3: Monitoring and Error Tracking Setup

#### Objective
Implement comprehensive monitoring, error tracking, and alerting before production deployment.

#### Implementation Tasks

**1. Sentry Error Monitoring Configuration**
```python
# File: config/settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(
            transaction_style='url',
            middleware_spans=True,
            signals_spans=False,
        ),
        RedisIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
    send_default_pii=False,  # Don't send user data
    environment='production',
)
```

**2. Health Check Endpoints**
```python
# File: apps/core/health_checks.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import requests

def health_check(request):
    """Comprehensive health check for production monitoring."""
    checks = {
        'database': check_database(),
        'cache': check_redis_cache(),
        'notion_api': check_notion_api(),
        'disk_space': check_disk_space(),
        'memory_usage': check_memory_usage()
    }
    
    overall_status = all(checks.values())
    status_code = 200 if overall_status else 503
    
    return JsonResponse({
        'status': 'healthy' if overall_status else 'unhealthy',
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    }, status=status_code)

def check_database():
    """Check database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception:
        return False

def check_redis_cache():
    """Check Redis cache connectivity."""
    try:
        cache.set('health_check', 'ok', 10)
        return cache.get('health_check') == 'ok'
    except Exception:
        return False

def check_notion_api():
    """Check Notion API connectivity."""
    try:
        # Test API call with timeout
        response = requests.get(
            'https://api.notion.com/v1/users/me',
            headers={'Authorization': f'Bearer {settings.NOTION_TOKEN}'},
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False
```

**3. Performance Monitoring**
```python
# File: apps/core/middleware.py
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('performance')

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor request performance and log slow requests."""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests (>2 seconds)
            if duration > 2.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s"
                )
            
            # Add performance header for monitoring
            response['X-Response-Time'] = f"{duration:.3f}"
        
        return response
```

**Quality Gate**: Monitoring captures and alerts on all critical error scenarios

---

## Parallel Development Streams

These streams can execute concurrently with the Critical Path:

### Stream A: Infrastructure Automation

#### CI/CD Pipeline Implementation
```yaml
# File: .github/workflows/production-deploy.yml
name: Production Deployment

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run security checks
      run: |
        pip install bandit safety
        bandit -r src/
        safety check
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        cd src
        python manage.py test --settings=config.settings.test
    
    - name: Run coverage report
      run: |
        pip install coverage
        cd src
        coverage run --source='.' manage.py test --settings=config.settings.test
        coverage report --fail-under=80

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build-and-deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    # Frontend Build Process
    - name: Setup Node.js for Frontend Build
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: 'src/package-lock.json'
    
    - name: Install Frontend Dependencies
      working-directory: ./src
      run: |
        npm ci --production
    
    - name: Build TailwindCSS and Frontend Assets
      working-directory: ./src
      run: |
        npm run build-css
        
    # Verify frontend build completed
    - name: Verify Frontend Build
      working-directory: ./src
      run: |
        ls -la static/css/output.css
        echo "Frontend build verification: $(wc -c < static/css/output.css) bytes"
    
    - name: Build Docker image
      run: |
        docker build -t bm-parliament:${{ github.sha }} ./src
    
    - name: Deploy to production
      env:
        DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
        DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        # Deploy using secure SSH with deployment scripts
        echo "$DEPLOY_KEY" | base64 -d > deploy_key
        chmod 600 deploy_key
        
        scp -i deploy_key -o StrictHostKeyChecking=no \
          deployment/deploy.sh $DEPLOY_USER@$DEPLOY_HOST:/tmp/
        
        ssh -i deploy_key -o StrictHostKeyChecking=no \
          $DEPLOY_USER@$DEPLOY_HOST \
          "cd /var/www/bm-parliament && /tmp/deploy.sh ${{ github.sha }}"
```

#### Enhanced Deployment Scripts
```bash
# File: deployment/scripts/deploy.sh (updated for current project structure)
#!/bin/bash
# Enhanced production deployment script

set -e  # Exit on any error

IMAGE_TAG=${1:-latest}
BACKUP_DIR="/var/backups/bm-parliament"
APP_DIR="/var/www/bm-parliament"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    if [ $DISK_USAGE -gt 85 ]; then
        log "ERROR: Disk usage is ${DISK_USAGE}%. Deployment aborted."
        exit 1
    fi
    
    # Check if required environment variables are set
    if [ -z "$DATABASE_URL" ] || [ -z "$DJANGO_SECRET_KEY" ]; then
        log "ERROR: Required environment variables not set"
        exit 1
    fi
    
    # Test database connectivity
    if ! python manage.py check --database default; then
        log "ERROR: Database connectivity check failed"
        exit 1
    fi
    
    log "Pre-deployment checks passed"
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    # Backup database
    pg_dump $DATABASE_URL > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    
    # Backup media files
    tar -czf "$BACKUP_FILE" -C "$APP_DIR" media staticfiles
    
    log "Backup created: $BACKUP_FILE"
}

# Deploy new version
deploy() {
    log "Deploying new version: $IMAGE_TAG"
    
    cd "$APP_DIR"
    
    # Pull new image
    docker-compose pull web
    
    # Build frontend assets (TailwindCSS + Font Awesome)
    log "Building frontend assets..."
    docker-compose run --rm web sh -c "
        cd /app &&
        npm install &&
        npm run build-css &&
        echo 'Frontend build completed successfully'
    "
    
    # Run database migrations
    docker-compose run --rm web python manage.py migrate --no-input
    
    # Collect static files (includes compiled CSS)
    docker-compose run --rm web python manage.py collectstatic --no-input
    
    # Restart services with zero downtime
    docker-compose up -d --no-deps web
    
    # Wait for application to be ready
    sleep 10
    
    # Health check
    if ! curl -f http://localhost:3000/health/ > /dev/null 2>&1; then
        log "ERROR: Health check failed, rolling back..."
        rollback_deployment
        exit 1
    fi
    
    log "Deployment successful"
}

# Rollback deployment
rollback_deployment() {
    log "Rolling back deployment..."
    
    # Find previous image
    PREVIOUS_IMAGE=$(docker images bm-parliament --format "table {{.Tag}}" | sed -n '2p')
    
    if [ -n "$PREVIOUS_IMAGE" ]; then
        # Rollback to previous version
        docker-compose stop web
        docker tag bm-parliament:$PREVIOUS_IMAGE bm-parliament:latest
        docker-compose up -d web
        
        log "Rollback completed to $PREVIOUS_IMAGE"
    else
        log "ERROR: No previous image found for rollback"
    fi
}

# Post-deployment checks
post_deployment_checks() {
    log "Running post-deployment checks..."
    
    # Check application health
    if curl -f http://localhost:3000/health/ > /dev/null 2>&1; then
        log "Application health check: PASSED"
    else
        log "Application health check: FAILED"
        return 1
    fi
    
    # Check database connectivity
    if docker-compose exec web python manage.py check --database default; then
        log "Database connectivity check: PASSED"
    else
        log "Database connectivity check: FAILED"
        return 1
    fi
    
    # Check static files
    if curl -f http://localhost:3000/static/css/output.css > /dev/null 2>&1; then
        log "Static files check: PASSED"
    else
        log "Static files check: FAILED"
        return 1
    fi
    
    # Check Font Awesome icons are loaded
    if curl -f http://localhost:3000/static/css/output.css | grep -q "Font Awesome"; then
        log "Font Awesome icons check: PASSED"
    else
        log "Font Awesome icons check: FAILED"
        return 1
    fi
    
    log "Post-deployment checks passed"
}

# Main deployment workflow
main() {
    log "Starting deployment of $IMAGE_TAG"
    
    pre_deployment_checks
    create_backup
    deploy
    post_deployment_checks
    
    log "Deployment completed successfully"
}

# Run deployment
main "$@"
```

### Stream B: Quality Assurance Expansion

#### Comprehensive Test Suite
```python
# File: tests/test_production_load.py
import asyncio
import aiohttp
import time
from django.test import LiveServerTestCase

class LoadTestCase(LiveServerTestCase):
    """Load testing for production readiness."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url
    
    async def make_request(self, session, url):
        """Make a single HTTP request."""
        start_time = time.time()
        try:
            async with session.get(url) as response:
                await response.text()
                return {
                    'status': response.status,
                    'duration': time.time() - start_time,
                    'success': response.status == 200
                }
        except Exception as e:
            return {
                'status': 0,
                'duration': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def load_test(self, url, concurrent_requests=50, total_requests=1000):
        """Perform load test on specific endpoint."""
        connector = aiohttp.TCPConnector(limit=100)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for i in range(total_requests):
                task = asyncio.create_task(
                    self.make_request(session, f"{self.base_url}{url}")
                )
                tasks.append(task)
                
                # Control concurrency
                if len(tasks) >= concurrent_requests:
                    results = await asyncio.gather(*tasks)
                    tasks = []
                    
                    # Analyze results
                    success_rate = sum(1 for r in results if r['success']) / len(results)
                    avg_duration = sum(r['duration'] for r in results) / len(results)
                    
                    # Assertions
                    self.assertGreater(success_rate, 0.95, "Success rate below 95%")
                    self.assertLess(avg_duration, 2.0, "Average response time > 2 seconds")
            
            # Process remaining tasks
            if tasks:
                results = await asyncio.gather(*tasks)
                success_rate = sum(1 for r in results if r['success']) / len(results)
                self.assertGreater(success_rate, 0.95)
    
    def test_homepage_load(self):
        """Test homepage under load."""
        asyncio.run(self.load_test('/', concurrent_requests=25, total_requests=500))
    
    def test_registration_load(self):
        """Test registration page under load."""
        asyncio.run(self.load_test('/member-registration/', concurrent_requests=10, total_requests=100))
```

#### Security Testing Suite
```python
# File: tests/test_security.py
from django.test import TestCase, Client
from django.urls import reverse
import requests

class SecurityTestCase(TestCase):
    """Security testing for production deployment."""
    
    def setUp(self):
        self.client = Client()
    
    def test_xss_protection(self):
        """Test XSS protection is working."""
        xss_payload = "<script>alert('xss')</script>"
        
        response = self.client.post(reverse('member_registration'), {
            'first_name': xss_payload,
            'last_name': 'Test',
            'email': 'test@example.com'
        })
        
        # Should not contain unescaped script tags
        self.assertNotContains(response, "<script>alert('xss')</script>")
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection."""
        sql_payload = "'; DROP TABLE users; --"
        
        response = self.client.get(reverse('chapter_list'), {
            'search': sql_payload
        })
        
        # Should return normal response, not error
        self.assertEqual(response.status_code, 200)
    
    def test_csrf_protection(self):
        """Test CSRF protection is enabled."""
        # Attempt POST without CSRF token
        response = self.client.post(reverse('member_registration'), {
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        # Should be rejected due to missing CSRF token
        self.assertEqual(response.status_code, 403)
    
    def test_rate_limiting(self):
        """Test rate limiting is working."""
        url = reverse('login')
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = self.client.post(url, {
                'username': 'invalid',
                'password': 'invalid'
            })
            responses.append(response.status_code)
        
        # Should eventually get rate limited
        self.assertIn(429, responses[-5:], "Rate limiting not working")
    
    def test_secure_headers(self):
        """Test security headers are set."""
        response = self.client.get('/')
        
        # Check for important security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
```

### Stream C: Documentation & Compliance

#### Automated API Documentation
```python
# File: apps/core/api_docs.py
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import json

def api_documentation(request):
    """Auto-generated API documentation from URL patterns."""
    
    from django.urls import get_resolver
    resolver = get_resolver()
    
    api_endpoints = []
    
    def extract_endpoints(url_patterns, prefix=''):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # Nested URL patterns
                extract_endpoints(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                # Individual URL pattern
                if hasattr(pattern, 'callback'):
                    endpoint = {
                        'name': pattern.name,
                        'pattern': prefix + str(pattern.pattern),
                        'view': pattern.callback.__name__ if pattern.callback else None,
                        'methods': getattr(pattern.callback, 'http_method_names', ['GET']),
                        'description': getattr(pattern.callback, '__doc__', '').strip()
                    }
                    api_endpoints.append(endpoint)
    
    extract_endpoints(resolver.url_patterns)
    
    # Filter API endpoints only
    api_endpoints = [ep for ep in api_endpoints if '/api/' in ep['pattern']]
    
    documentation = {
        'title': 'BM Parliament API Documentation',
        'version': '1.0.0',
        'base_url': request.build_absolute_uri('/api/'),
        'endpoints': api_endpoints,
        'authentication': {
            'type': 'Session-based',
            'login_url': reverse('login'),
            'logout_url': reverse('logout')
        },
        'response_format': 'JSON',
        'error_codes': {
            '400': 'Bad Request - Invalid parameters',
            '401': 'Unauthorized - Authentication required',
            '403': 'Forbidden - Insufficient permissions',
            '404': 'Not Found - Resource does not exist',
            '429': 'Too Many Requests - Rate limited',
            '500': 'Internal Server Error - Server error'
        }
    }
    
    return JsonResponse(documentation, indent=2)
```

### Stream D: Performance & Scalability

#### Database Optimization
```python
# File: apps/core/management/commands/optimize_db.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Optimize database for production performance'
    
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Create production indexes
            production_indexes = [
                # User-related indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users_user (email) WHERE is_active = true;",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_type_active ON users_user (user_type) WHERE is_active = true;",
                
                # Chapter-related indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chapters_status_tier ON chapters_chapter (status, tier);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chapter_membership_status ON chapters_chaptermembership (status, chapter_id);",
                
                # Referral-related indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referrals_status_date ON referrals_referral (status, created_at);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_referrals_user_status ON referrals_referral (user_id, status);",
                
                # Performance indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expire_date ON django_session (expire_date);",
            ]
            
            for index_sql in production_indexes:
                try:
                    self.stdout.write(f"Creating index: {index_sql}")
                    cursor.execute(index_sql)
                    self.stdout.write(self.style.SUCCESS("✓ Index created successfully"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Index creation skipped: {e}"))
            
            # Update table statistics
            cursor.execute("ANALYZE;")
            self.stdout.write(self.style.SUCCESS("✓ Database statistics updated"))
            
            self.stdout.write(self.style.SUCCESS("Database optimization completed"))
```

#### Cache Optimization
```python
# File: apps/core/cache_utils.py
from django.core.cache import cache
from django.conf import settings
import hashlib
import json

class CacheManager:
    """Centralized cache management for production performance."""
    
    @staticmethod
    def cache_key(prefix, *args, **kwargs):
        """Generate consistent cache keys."""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        
        # Hash long keys to prevent key length issues
        if len(key_data) > 200:
            key_data = hashlib.md5(key_data.encode()).hexdigest()
        
        return key_data
    
    @staticmethod
    def cache_page_for_user(user_type, page_name, timeout=300):
        """Cache pages based on user type."""
        def decorator(view_func):
            def wrapper(request, *args, **kwargs):
                if request.user.is_authenticated:
                    cache_key = CacheManager.cache_key(
                        'page_cache',
                        user_type,
                        page_name,
                        request.user.id
                    )
                else:
                    cache_key = CacheManager.cache_key(
                        'page_cache',
                        'anonymous',
                        page_name
                    )
                
                # Try to get from cache
                cached_response = cache.get(cache_key)
                if cached_response:
                    return cached_response
                
                # Generate response and cache it
                response = view_func(request, *args, **kwargs)
                if response.status_code == 200:
                    cache.set(cache_key, response, timeout)
                
                return response
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all cache entries for a specific user."""
        # This would require a more sophisticated cache backend
        # For now, we'll clear specific known patterns
        patterns = ['page_cache', 'user_data', 'user_permissions']
        for pattern in patterns:
            cache_key = CacheManager.cache_key(pattern, user_id)
            cache.delete(cache_key)
```

---

## Quality Assurance Framework

### Testing Standards

#### Test Coverage Requirements
- **Critical Path Functions**: 95% coverage minimum
- **Security Functions**: 100% coverage required
- **API Endpoints**: 90% coverage minimum
- **User Workflows**: End-to-end coverage for all major paths

#### Testing Types
```python
# File: tests/test_framework.py
class ProductionTestSuite:
    """Comprehensive testing framework for production deployment."""
    
    def __init__(self):
        self.test_categories = {
            'unit': 'Individual function/method testing',
            'integration': 'Component interaction testing', 
            'security': 'Security vulnerability testing',
            'performance': 'Load and stress testing',
            'e2e': 'End-to-end user workflow testing',
            'accessibility': 'WCAG compliance testing',
            'mobile': 'Mobile device compatibility testing'
        }
    
    def run_production_test_suite(self):
        """Run complete test suite for production readiness."""
        results = {}
        
        for test_type, description in self.test_categories.items():
            print(f"Running {test_type} tests: {description}")
            results[test_type] = self.run_test_category(test_type)
        
        return self.generate_test_report(results)
    
    def run_test_category(self, category):
        """Run specific category of tests."""
        # Implementation would call appropriate test runners
        pass
    
    def generate_test_report(self, results):
        """Generate comprehensive test report."""
        report = {
            'overall_status': all(results.values()),
            'detailed_results': results,
            'recommendations': self.get_recommendations(results),
            'timestamp': datetime.now().isoformat()
        }
        return report
```

### Continuous Quality Monitoring

#### Performance Benchmarks
```python
# File: apps/core/performance_benchmarks.py
from django.test import TestCase
from django.test.utils import override_settings
import time

class PerformanceBenchmarks(TestCase):
    """Performance benchmarks for production deployment."""
    
    def setUp(self):
        # Create test data
        self.create_test_data()
    
    def test_homepage_performance(self):
        """Homepage should load in under 1 second."""
        start_time = time.time()
        response = self.client.get('/')
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0, f"Homepage took {duration:.2f}s")
    
    def test_database_query_performance(self):
        """Database queries should be optimized."""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            # Perform operation that should be optimized
            response = self.client.get('/chapters/')
            
            # Check query count
            query_count = len(connection.queries)
            self.assertLess(query_count, 10, f"Too many queries: {query_count}")
            
            # Check for N+1 problems
            select_queries = [q for q in connection.queries if q['sql'].startswith('SELECT')]
            self.assertLess(len(select_queries), 5, "Possible N+1 query problem")
    
    def test_cache_performance(self):
        """Cache should improve performance significantly."""
        from django.core.cache import cache
        
        # Test cache hit performance
        cache.set('test_key', 'test_value', 300)
        
        start_time = time.time()
        cached_value = cache.get('test_key')
        cache_duration = time.time() - start_time
        
        self.assertEqual(cached_value, 'test_value')
        self.assertLess(cache_duration, 0.01, "Cache access too slow")
```

---

## Security & Compliance

### Security Checklist

#### Production Security Requirements
- [ ] **HTTPS enforced** with HSTS headers
- [ ] **Security headers** configured (CSP, XSS protection, etc.)
- [ ] **Rate limiting** implemented on all public endpoints
- [ ] **CSRF protection** enabled on all forms
- [ ] **SQL injection protection** verified
- [ ] **XSS protection** tested and confirmed
- [ ] **File upload security** implemented
- [ ] **Session security** configured (secure cookies, timeouts)
- [ ] **Password policy** enforced (complexity, history)
- [ ] **MFA available** for administrative accounts

#### Security Configuration
```python
# File: config/settings/security.py
"""Production security settings."""

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800  # 30 minutes

# CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']

# Password Security
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.users.security.PasswordStrengthValidator',
        'OPTIONS': {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_symbols': True,
        }
    },
]
```

### Compliance Documentation

#### Privacy Policy Implementation
```python
# File: apps/core/privacy.py
from django.http import JsonResponse
from django.shortcuts import render

def privacy_policy(request):
    """Display privacy policy with user consent tracking."""
    context = {
        'last_updated': 'June 2025',
        'data_retention_policy': {
            'user_accounts': '7 years after last activity',
            'service_requests': '5 years for audit purposes',
            'session_data': '30 days',
            'log_files': '1 year'
        },
        'data_sharing': {
            'government_agencies': 'As required by law for service delivery',
            'third_parties': 'No sharing with commercial third parties',
            'international': 'No international data transfers'
        },
        'user_rights': [
            'Right to access personal data',
            'Right to correct inaccurate data',
            'Right to delete account and data',
            'Right to data portability',
            'Right to withdraw consent'
        ]
    }
    return render(request, 'core/privacy_policy.html', context)

def data_deletion_request(request):
    """Handle user data deletion requests."""
    if request.method == 'POST':
        # Log the deletion request
        import logging
        logger = logging.getLogger('privacy')
        logger.info(f"Data deletion requested by user {request.user.id}")
        
        # Create deletion task (to be processed by admin)
        from apps.core.models import DataDeletionRequest
        DataDeletionRequest.objects.create(
            user=request.user,
            reason=request.POST.get('reason', ''),
            requested_at=timezone.now()
        )
        
        return JsonResponse({'status': 'success', 'message': 'Deletion request submitted'})
    
    return render(request, 'core/data_deletion_form.html')
```

---

## Monitoring & Operations

### Production Monitoring Setup

Building on the existing `monitoring_guide.md`, implement enhanced monitoring:

#### Sentry Integration
```python
# File: config/settings/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Sentry configuration
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(
            transaction_style='url',
            middleware_spans=True,
        ),
        sentry_logging,
    ],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment='production',
    before_send=lambda event, hint: filter_sensitive_data(event, hint)
)

def filter_sensitive_data(event, hint):
    """Filter sensitive data from Sentry events."""
    # Remove sensitive data from event
    if 'request' in event:
        if 'data' in event['request']:
            sensitive_fields = ['password', 'token', 'secret', 'key']
            for field in sensitive_fields:
                if field in event['request']['data']:
                    event['request']['data'][field] = '[Filtered]'
    
    return event
```

#### Custom Monitoring Dashboard
```python
# File: apps/core/monitoring_dashboard.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.core.cache import cache
import psutil
import os

@staff_member_required
def monitoring_dashboard(request):
    """Real-time monitoring dashboard for production."""
    
    # System metrics
    system_metrics = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'uptime': psutil.boot_time()
    }
    
    # Database metrics
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections
            FROM pg_stat_activity;
        """)
        db_metrics = cursor.fetchone()
    
    # Application metrics
    from django.contrib.auth import get_user_model
    from apps.referrals.models import Referral
    from apps.chapters.models import Chapter
    
    User = get_user_model()
    
    app_metrics = {
        'total_users': User.objects.count(),
        'active_users_today': User.objects.filter(
            last_login__date=timezone.now().date()
        ).count(),
        'pending_referrals': Referral.objects.filter(status='pending').count(),
        'active_chapters': Chapter.objects.filter(status='active').count(),
    }
    
    # Cache metrics
    try:
        cache_stats = cache._cache.get_stats()
        cache_metrics = {
            'hits': cache_stats.get('hits', 0),
            'misses': cache_stats.get('misses', 0),
            'hit_rate': cache_stats.get('hits', 0) / (cache_stats.get('hits', 1) + cache_stats.get('misses', 1)) * 100
        }
    except:
        cache_metrics = {'error': 'Unable to retrieve cache stats'}
    
    context = {
        'system_metrics': system_metrics,
        'db_metrics': db_metrics,
        'app_metrics': app_metrics,
        'cache_metrics': cache_metrics,
        'refresh_interval': 30  # Auto-refresh every 30 seconds
    }
    
    return render(request, 'admin/monitoring_dashboard.html', context)
```

#### Alert Configuration
```python
# File: apps/core/alerts.py
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('alerts')

class AlertManager:
    """Production alert management system."""
    
    ALERT_LEVELS = {
        'CRITICAL': {'priority': 1, 'response_time': '15 minutes'},
        'HIGH': {'priority': 2, 'response_time': '1 hour'},
        'MEDIUM': {'priority': 3, 'response_time': '4 hours'},
        'LOW': {'priority': 4, 'response_time': 'next business day'}
    }
    
    @staticmethod
    def send_alert(level, message, details=None):
        """Send alert to appropriate channels."""
        if level not in AlertManager.ALERT_LEVELS:
            level = 'MEDIUM'
        
        alert_info = AlertManager.ALERT_LEVELS[level]
        
        # Log alert
        logger.error(f"[{level}] {message}", extra={'details': details})
        
        # Send email for critical and high alerts
        if level in ['CRITICAL', 'HIGH']:
            AlertManager._send_email_alert(level, message, details)
        
        # Send SMS for critical alerts only
        if level == 'CRITICAL':
            AlertManager._send_sms_alert(message)
    
    @staticmethod
    def _send_email_alert(level, message, details):
        """Send email alert."""
        subject = f"[{level}] BM Parliament Alert: {message}"
        
        email_body = f"""
        Alert Level: {level}
        Message: {message}
        Response Time Required: {AlertManager.ALERT_LEVELS[level]['response_time']}
        
        Details:
        {details or 'No additional details provided'}
        
        Timestamp: {timezone.now()}
        
        Please respond according to the incident response procedures.
        """
        
        recipient_list = settings.ALERT_EMAIL_RECIPIENTS
        
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
    
    @staticmethod
    def _send_sms_alert(message):
        """Send SMS alert for critical issues."""
        # Implementation would depend on SMS service provider
        # This is a placeholder for SMS integration
        logger.info(f"SMS alert would be sent: {message}")

# Usage examples
def check_system_health():
    """System health check with alerting."""
    import psutil
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 90:
        AlertManager.send_alert(
            'CRITICAL',
            f'High CPU usage: {cpu_percent}%',
            {'cpu_percent': cpu_percent, 'threshold': 90}
        )
    elif cpu_percent > 80:
        AlertManager.send_alert(
            'HIGH',
            f'Elevated CPU usage: {cpu_percent}%',
            {'cpu_percent': cpu_percent, 'threshold': 80}
        )
    
    # Check memory usage
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 95:
        AlertManager.send_alert(
            'CRITICAL',
            f'High memory usage: {memory_percent}%',
            {'memory_percent': memory_percent, 'threshold': 95}
        )
    
    # Check disk space
    disk_percent = psutil.disk_usage('/').percent
    if disk_percent > 90:
        AlertManager.send_alert(
            'HIGH',
            f'Low disk space: {disk_percent}% used',
            {'disk_percent': disk_percent, 'threshold': 90}
        )
```

---

## Go-Live Procedures

### Pre-Launch Checklist

#### Final Verification Steps
```bash
#!/bin/bash
# File: deployment/scripts/pre_launch_checklist.sh

echo "=== BM Parliament Pre-Launch Checklist ==="
echo "Timestamp: $(date)"

ERRORS=0

# Function to check status
check_status() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1"
        ((ERRORS++))
    fi
}

echo "--- Environment Checks ---"

# Check environment variables
if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo "❌ DJANGO_SECRET_KEY not set"
    ((ERRORS++))
else
    echo "✅ DJANGO_SECRET_KEY configured"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    ((ERRORS++))
else
    echo "✅ DATABASE_URL configured"
fi

# Check SSL certificate
openssl s_client -connect bm-parliament.gov.ph:443 -servername bm-parliament.gov.ph </dev/null 2>/dev/null | openssl x509 -noout -dates
check_status "SSL certificate valid"

echo "--- Security Checks ---"

# Check security headers
HEADERS=$(curl -I https://bm-parliament.gov.ph 2>/dev/null)
echo "$HEADERS" | grep -i "strict-transport-security" > /dev/null
check_status "HSTS header present"

echo "$HEADERS" | grep -i "x-content-type-options" > /dev/null
check_status "X-Content-Type-Options header present"

echo "$HEADERS" | grep -i "x-frame-options" > /dev/null
check_status "X-Frame-Options header present"

echo "--- Application Checks ---"

# Check application health
curl -f https://bm-parliament.gov.ph/health/ > /dev/null 2>&1
check_status "Application health check"

# Check database connectivity
python manage.py check --database default > /dev/null 2>&1
check_status "Database connectivity"

# Check static files
curl -f https://bm-parliament.gov.ph/static/css/output.css > /dev/null 2>&1
check_status "Static files accessible"

# Check Font Awesome icons
curl -s https://bm-parliament.gov.ph/static/css/output.css | grep -q "Font Awesome" || \
curl -s https://bm-parliament.gov.ph/ | grep -q "font-awesome"
check_status "Font Awesome icons loaded"

echo "--- Performance Checks ---"

# Check response time
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' https://bm-parliament.gov.ph/)
if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
    echo "✅ Response time: ${RESPONSE_TIME}s"
else
    echo "❌ Response time too slow: ${RESPONSE_TIME}s"
    ((ERRORS++))
fi

echo "--- Monitoring Checks ---"

# Check Sentry configuration
if [ -z "$SENTRY_DSN" ]; then
    echo "❌ Sentry not configured"
    ((ERRORS++))
else
    echo "✅ Sentry configured"
fi

# Check log files
if [ -f "/var/log/bm-parliament/error.log" ]; then
    echo "✅ Error logging configured"
else
    echo "❌ Error logging not configured"
    ((ERRORS++))
fi

echo "--- Backup Checks ---"

# Check backup system
if [ -d "/var/backups/bm-parliament" ]; then
    LATEST_BACKUP=$(find /var/backups/bm-parliament -name "*.tar.gz" -mtime -1 | wc -l)
    if [ $LATEST_BACKUP -gt 0 ]; then
        echo "✅ Recent backup available"
    else
        echo "❌ No recent backup found"
        ((ERRORS++))
    fi
else
    echo "❌ Backup directory not found"
    ((ERRORS++))
fi

echo "--- Summary ---"
if [ $ERRORS -eq 0 ]; then
    echo "🎉 All checks passed! Ready for production launch."
    exit 0
else
    echo "⚠️  $ERRORS issues found. Please resolve before launch."
    exit 1
fi
```

### Launch Day Procedures

#### Launch Sequence
```bash
#!/bin/bash
# File: deployment/scripts/launch_sequence.sh

set -e

echo "=== BM Parliament Production Launch Sequence ==="
echo "Starting at: $(date)"

# Step 1: Final backup
echo "Step 1: Creating pre-launch backup..."
./backup.sh pre-launch

# Step 2: Deploy latest version
echo "Step 2: Deploying production version..."
./deploy.sh production

# Step 3: Run final tests
echo "Step 3: Running post-deployment tests..."
python manage.py test --settings=config.settings.production

# Step 4: Update DNS (if needed)
echo "Step 4: DNS configuration..."
# This would be done manually or through DNS provider API

# Step 5: Enable monitoring
echo "Step 5: Enabling production monitoring..."
# Start monitoring services
systemctl start bm-parliament-monitor

# Step 6: Send launch notification
echo "Step 6: Sending launch notifications..."
python manage.py send_launch_notification

echo "🚀 Production launch completed successfully!"
echo "Monitoring dashboard: https://bm-parliament.gov.ph/admin/monitoring/"
```

---

## Post-Launch Operations

### Continuous Monitoring

#### Daily Operations Checklist
```bash
#!/bin/bash
# File: deployment/scripts/daily_operations.sh

echo "=== Daily Operations Check - $(date) ==="

# Check system health
echo "1. System Health Check"
python manage.py health_check

# Check error logs
echo "2. Error Log Review"
tail -n 100 /var/log/bm-parliament/error.log | grep -i error || echo "No errors found"

# Check performance metrics
echo "3. Performance Metrics"
python manage.py performance_report

# Check backup status
echo "4. Backup Status"
./verify_backup.sh

# Check SSL certificate expiry
echo "5. SSL Certificate Check"
openssl s_client -connect bm-parliament.gov.ph:443 -servername bm-parliament.gov.ph </dev/null 2>/dev/null | openssl x509 -noout -dates

# Generate daily report
echo "6. Generating Daily Report"
python manage.py daily_report --email
```

#### Weekly Maintenance
```python
# File: apps/core/management/commands/weekly_maintenance.py
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Weekly maintenance tasks for production system'
    
    def handle(self, *args, **options):
        self.stdout.write("Starting weekly maintenance...")
        
        # 1. Database maintenance
        self.stdout.write("1. Database maintenance")
        with connection.cursor() as cursor:
            # Update table statistics
            cursor.execute("ANALYZE;")
            
            # Clean old sessions
            cursor.execute("DELETE FROM django_session WHERE expire_date < NOW();")
            
            # Clean old log entries (keep 30 days)
            cursor.execute("""
                DELETE FROM django_admin_log 
                WHERE action_time < NOW() - INTERVAL '30 days';
            """)
        
        # 2. Cache maintenance
        self.stdout.write("2. Cache maintenance")
        cache.clear()  # Clear all cache entries
        
        # 3. File cleanup
        self.stdout.write("3. File cleanup")
        import os
        import glob
        from datetime import datetime, timedelta
        
        # Clean old temporary files
        temp_files = glob.glob('/tmp/bmparliament_*')
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for temp_file in temp_files:
            file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
            if file_time < cutoff_date:
                os.remove(temp_file)
                self.stdout.write(f"Removed old temp file: {temp_file}")
        
        # 4. Performance analysis
        self.stdout.write("4. Performance analysis")
        # Generate weekly performance report
        
        # 5. Security audit
        self.stdout.write("5. Security audit")
        # Run automated security checks
        
        self.stdout.write(self.style.SUCCESS("Weekly maintenance completed"))
```

### Incident Response

#### Incident Response Procedures
```python
# File: apps/core/incident_response.py
from django.core.management.base import BaseCommand
from apps.core.alerts import AlertManager
import logging

logger = logging.getLogger('incidents')

class IncidentResponse:
    """Automated incident response system."""
    
    INCIDENT_TYPES = {
        'high_cpu': {
            'threshold': 90,
            'action': 'restart_services',
            'alert_level': 'HIGH'
        },
        'high_memory': {
            'threshold': 95,
            'action': 'clear_cache_restart',
            'alert_level': 'CRITICAL'
        },
        'database_down': {
            'threshold': None,
            'action': 'restart_database',
            'alert_level': 'CRITICAL'
        },
        'application_down': {
            'threshold': None,
            'action': 'restart_application',
            'alert_level': 'CRITICAL'
        }
    }
    
    @staticmethod
    def handle_incident(incident_type, metrics=None):
        """Handle specific incident type."""
        if incident_type not in IncidentResponse.INCIDENT_TYPES:
            logger.error(f"Unknown incident type: {incident_type}")
            return False
        
        incident_config = IncidentResponse.INCIDENT_TYPES[incident_type]
        
        # Log incident
        logger.critical(f"Incident detected: {incident_type}", extra={'metrics': metrics})
        
        # Send alert
        AlertManager.send_alert(
            incident_config['alert_level'],
            f"Incident: {incident_type}",
            {'metrics': metrics, 'automated_action': incident_config['action']}
        )
        
        # Execute automated response
        action_method = getattr(IncidentResponse, incident_config['action'], None)
        if action_method:
            try:
                action_method()
                logger.info(f"Automated response executed: {incident_config['action']}")
                return True
            except Exception as e:
                logger.error(f"Automated response failed: {str(e)}")
                return False
        
        return False
    
    @staticmethod
    def restart_services():
        """Restart application services."""
        import subprocess
        subprocess.run(['docker-compose', 'restart', 'web'], check=True)
    
    @staticmethod
    def clear_cache_restart():
        """Clear cache and restart services."""
        from django.core.cache import cache
        cache.clear()
        IncidentResponse.restart_services()
    
    @staticmethod
    def restart_database():
        """Restart database service."""
        import subprocess
        subprocess.run(['docker-compose', 'restart', 'db'], check=True)
    
    @staticmethod
    def restart_application():
        """Full application restart."""
        import subprocess
        subprocess.run(['docker-compose', 'restart'], check=True)
```

---

## Troubleshooting & Support

### Critical: CSRF Verification Failed (Production Deployment Issue)

**Symptoms:**
- All forms return "CSRF verification failed. Request aborted" 
- User registration, login, and contact forms fail with 403 errors
- Production deployment appears successful but forms don't work

**Root Cause:**
Missing or incorrect `DJANGO_SETTINGS_MODULE` environment variable causes Django to use base settings instead of production settings, breaking CSRF configuration.

**Immediate Solution:**
```bash
# 1. Verify DJANGO_SETTINGS_MODULE is set correctly in production
docker exec bmparliament_web env | grep DJANGO_SETTINGS_MODULE
# Must output: DJANGO_SETTINGS_MODULE=config.settings.production

# 2. If missing or incorrect, add to environment variables:
DJANGO_SETTINGS_MODULE=config.settings.production

# 3. Verify production settings are loaded correctly
docker exec bmparliament_web python manage.py shell -c "
from django.conf import settings
print('Settings Module:', settings.SETTINGS_MODULE)
print('CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('DEBUG:', settings.DEBUG)
"

# 4. Restart containers after environment variable changes
docker-compose down && docker-compose up -d

# 5. Test forms functionality immediately
curl -I https://bm-parliament.gov.ph/accounts/login/
# Should return 200 OK, not 403 Forbidden
```

**Prevention:**
- Always set `DJANGO_SETTINGS_MODULE=config.settings.production` as the FIRST environment variable
- Test all forms after deployment to verify CSRF protection works correctly
- Include this check in deployment verification scripts
- Monitor application logs for CSRF-related error messages

---

### Common Issues and Solutions

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec db pg_isready -U bmparliament_user -d bmparliament_db

# Check connection pool
docker-compose exec web python manage.py dbshell
\l  # List databases
\conninfo  # Connection info
```

#### Performance Issues
```bash
# Check slow queries
docker-compose exec db psql -U bmparliament_user -d bmparliament_db -c "
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"

# Check index usage
docker-compose exec db psql -U bmparliament_user -d bmparliament_db -c "
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;"
```

#### SSL Certificate Issues
```bash
# Check certificate expiry
openssl s_client -connect bm-parliament.gov.ph:443 -servername bm-parliament.gov.ph </dev/null 2>/dev/null | openssl x509 -noout -dates

# Renew Let's Encrypt certificate
certbot renew --nginx

# Test SSL configuration
ssl-cert-check -c bm-parliament.gov.ph:443
```

### Support Procedures

#### Emergency Contacts
- **System Administrator**: admin@bm-parliament.gov.ph
- **Database Administrator**: dba@bm-parliament.gov.ph  
- **Security Team**: security@bmparliament.gov.ph
- **MP Office**: mp@bm-parliament.gov.ph

#### Escalation Matrix
1. **Level 1**: System alerts and automated responses
2. **Level 2**: On-call technical staff (response within 15 minutes)
3. **Level 3**: Senior technical team (response within 1 hour)
4. **Level 4**: Management and stakeholder notification

---

## Implementation Next Steps

### Immediate Actions Required

1. **Start Critical Path Implementation**
   ```bash
   # Begin with security hardening
   cd src
   # Enable security middleware in config/settings/base.py
   # Create production environment configuration
   # Set up SSL certificates
   ```

2. **Initialize Parallel Streams**
   ```bash
   # Set up CI/CD pipeline
   mkdir -p .github/workflows
   # Create GitHub Actions configuration
   
   # Begin test expansion
   mkdir -p tests/production
   # Create comprehensive test suites
   ```

3. **Configure Monitoring**
   ```bash
   # Set up Sentry
   pip install sentry-sdk
   # Configure error tracking
   
   # Create health check endpoints
   # Set up monitoring dashboard
   ```

### Success Metrics

The BM Parliament platform will be production-ready when:

- ✅ **Security**: All security audits pass with zero critical vulnerabilities
- ✅ **Performance**: All endpoints respond in <2 seconds under production load
- ✅ **Reliability**: 99.9% uptime achieved during 48-hour monitoring period  
- ✅ **Functionality**: All enabled features pass comprehensive end-to-end testing
- ✅ **Monitoring**: Complete error tracking and performance monitoring operational
- ✅ **Compliance**: All legal and privacy requirements implemented and documented

---

*Last Updated: June 2025*  
*Next Review: Upon completion of Critical Path items*  
*Document Version: 1.0*

**Prepared by**: BM Parliament Development Team  
**Approved for Implementation**: Ready for autonomous Claude Code execution