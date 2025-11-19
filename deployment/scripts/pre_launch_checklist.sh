#!/bin/bash
# Pre-Launch Checklist for #FahanieCares Platform
# This script performs comprehensive pre-deployment verification

set -e

echo "=== #FahanieCares Pre-Launch Checklist ==="
echo "Timestamp: $(date)"
echo "=========================================="

ERRORS=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        ((ERRORS++))
    fi
}

# Function to check warning
check_warning() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${YELLOW}⚠️  $1${NC}"
        ((WARNINGS++))
    fi
}

echo ""
echo "--- 1. Environment Configuration ---"

# Check environment variables
if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo -e "${RED}❌ DJANGO_SECRET_KEY not set${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ DJANGO_SECRET_KEY configured${NC}"
fi

if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ DATABASE_URL not set${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ DATABASE_URL configured${NC}"
fi

if [ -z "$REDIS_URL" ]; then
    echo -e "${YELLOW}⚠️  REDIS_URL not set (cache will use fallback)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅ REDIS_URL configured${NC}"
fi

if [ -z "$SENTRY_DSN" ]; then
    echo -e "${YELLOW}⚠️  SENTRY_DSN not set (error tracking disabled)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅ SENTRY_DSN configured${NC}"
fi

echo ""
echo "--- 2. Security Checks ---"

# Check Django debug mode
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    echo -e "${RED}❌ DEBUG mode is enabled in production!${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ DEBUG mode disabled${NC}"
fi

# Check ALLOWED_HOSTS
if [ -z "$ALLOWED_HOSTS" ]; then
    echo -e "${RED}❌ ALLOWED_HOSTS not configured${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ ALLOWED_HOSTS configured: $ALLOWED_HOSTS${NC}"
fi

# Check SSL certificate (if domain is accessible)
if [ ! -z "$PRODUCTION_DOMAIN" ]; then
    openssl s_client -connect ${PRODUCTION_DOMAIN}:443 -servername ${PRODUCTION_DOMAIN} </dev/null 2>/dev/null | openssl x509 -noout -dates > /dev/null 2>&1
    check_warning "SSL certificate valid for ${PRODUCTION_DOMAIN}"
fi

echo ""
echo "--- 3. Database Checks ---"

# Test database connectivity
cd /Users/macbookpro/Documents/fahanie-cares/src
python manage.py check --database default > /dev/null 2>&1
check_status "Database connectivity"

# Check for pending migrations
PENDING_MIGRATIONS=$(python manage.py showmigrations --plan | grep "\[ \]" | wc -l)
if [ $PENDING_MIGRATIONS -gt 0 ]; then
    echo -e "${RED}❌ ${PENDING_MIGRATIONS} pending migrations found${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ All migrations applied${NC}"
fi

echo ""
echo "--- 4. Static Files & Assets ---"

# Check if static files are collected
if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
    echo -e "${GREEN}✅ Static files collected${NC}"
else
    echo -e "${YELLOW}⚠️  Static files not collected (run collectstatic)${NC}"
    ((WARNINGS++))
fi

# Check TailwindCSS build
if [ -f "static/css/output.css" ]; then
    FILE_SIZE=$(wc -c < static/css/output.css)
    if [ $FILE_SIZE -gt 1000 ]; then
        echo -e "${GREEN}✅ TailwindCSS built (${FILE_SIZE} bytes)${NC}"
    else
        echo -e "${RED}❌ TailwindCSS output too small${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${RED}❌ TailwindCSS not built${NC}"
    ((ERRORS++))
fi

# Check Font Awesome
if [ -d "static/webfonts" ] && [ "$(ls -A static/webfonts)" ]; then
    echo -e "${GREEN}✅ Font Awesome webfonts present${NC}"
else
    echo -e "${RED}❌ Font Awesome webfonts missing${NC}"
    ((ERRORS++))
fi

echo ""
echo "--- 5. Application Health ---"

# Run Django system check
python manage.py check > /dev/null 2>&1
check_status "Django system check"

# Check if required apps are installed
python -c "import django; django.setup(); from django.apps import apps; print(len(apps.get_app_configs()))" > /dev/null 2>&1
check_status "Django apps configuration"

echo ""
echo "--- 6. Performance & Optimization ---"

# Check if database indexes exist
python manage.py dbshell -c "SELECT count(*) FROM pg_indexes WHERE schemaname = 'public';" > /dev/null 2>&1
check_warning "Database indexes configured"

# Check Redis connectivity (if configured)
if [ ! -z "$REDIS_URL" ]; then
    python -c "from django.core.cache import cache; cache.set('test', 'ok', 10); print(cache.get('test'))" > /dev/null 2>&1
    check_warning "Redis cache connectivity"
fi

echo ""
echo "--- 7. Backup & Recovery ---"

# Check backup directory
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares}"
if [ -d "$BACKUP_DIR" ]; then
    echo -e "${GREEN}✅ Backup directory exists${NC}"
else
    echo -e "${YELLOW}⚠️  Backup directory not found at $BACKUP_DIR${NC}"
    ((WARNINGS++))
fi

# Check AWS S3 credentials for backups
if [ ! -z "$AWS_ACCESS_KEY_ID" ] && [ ! -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${GREEN}✅ AWS S3 credentials configured${NC}"
else
    echo -e "${YELLOW}⚠️  AWS S3 credentials not configured (backups will be local only)${NC}"
    ((WARNINGS++))
fi

echo ""
echo "--- 8. Monitoring & Logging ---"

# Check log directory
LOG_DIR="${LOG_DIR:-/Users/macbookpro/Documents/fahanie-cares/src/logs}"
if [ -d "$LOG_DIR" ]; then
    echo -e "${GREEN}✅ Log directory exists${NC}"
else
    mkdir -p "$LOG_DIR"
    echo -e "${YELLOW}⚠️  Log directory created at $LOG_DIR${NC}"
fi

# Check Sentry configuration
if [ ! -z "$SENTRY_DSN" ]; then
    python -c "import sentry_sdk; print('Sentry OK')" > /dev/null 2>&1
    check_status "Sentry SDK configured"
fi

echo ""
echo "--- 9. Docker & Deployment ---"

# Check Docker daemon
docker info > /dev/null 2>&1
check_warning "Docker daemon running"

# Check Docker Compose
docker-compose version > /dev/null 2>&1
check_warning "Docker Compose available"

# Check if images can be built
cd /Users/macbookpro/Documents/fahanie-cares
docker-compose build --dry-run > /dev/null 2>&1
check_warning "Docker images can be built"

echo ""
echo "--- 10. Feature Flags ---"

# Check feature flags configuration
cd /Users/macbookpro/Documents/fahanie-cares/src
python -c "
from django.conf import settings
features = settings.FEATURES
print('Ministry Programs:', features.get('ministry_programs', False))
print('Chapters:', features.get('chapters', False))
print('Announcements:', features.get('announcements', False))
print('Staff Directory:', features.get('staff_directory', False))
print('Referral System:', features.get('referral_system', False), '(Disabled pending MOAs)')
" 2>/dev/null || echo -e "${RED}❌ Failed to check feature flags${NC}"

echo ""
echo "=========================================="
echo "--- Pre-Launch Summary ---"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED! Ready for production launch.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: ./deployment/scripts/launch_sequence.sh"
    echo "2. Monitor deployment at: https://[domain]/monitoring/"
    echo "3. Check health endpoint: https://[domain]/health/"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}✅ No critical errors found. ${WARNINGS} warnings to review.${NC}"
    echo ""
    echo "Warnings are non-critical and can be addressed post-launch."
    echo "Proceed with deployment if acceptable."
    exit 0
else
    echo -e "${RED}❌ ${ERRORS} CRITICAL ERRORS found. Please resolve before launch.${NC}"
    echo -e "${YELLOW}⚠️  ${WARNINGS} warnings also detected.${NC}"
    echo ""
    echo "Critical errors must be fixed before production deployment."
    exit 1
fi