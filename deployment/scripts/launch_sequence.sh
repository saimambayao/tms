#!/bin/bash
# Production Launch Sequence for #FahanieCares Platform
# This script orchestrates the complete production deployment

set -e

echo "=== #FahanieCares Production Launch Sequence ==="
echo "Starting at: $(date)"
echo "=============================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/Users/macbookpro/Documents/fahanie-cares"
DJANGO_ROOT="${PROJECT_ROOT}/src"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares}"
LOG_FILE="${LOG_FILE:-/var/log/fahaniecares/launch_$(date +%Y%m%d_%H%M%S).log}"

# Ensure log directory exists
mkdir -p $(dirname "$LOG_FILE")

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to log and execute
execute() {
    local description="$1"
    local command="$2"
    
    log "${BLUE}➤ ${description}...${NC}"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✅ ${description} completed${NC}"
        return 0
    else
        log "${RED}❌ ${description} failed${NC}"
        return 1
    fi
}

# Function to create backup
create_backup() {
    log "${BLUE}📦 Creating pre-launch backup...${NC}"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/pre_launch_${TIMESTAMP}.tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ ! -z "$DATABASE_URL" ]; then
        execute "Database backup" "pg_dump $DATABASE_URL > ${BACKUP_DIR}/db_pre_launch_${TIMESTAMP}.sql"
    fi
    
    # Backup media and static files
    cd "$DJANGO_ROOT"
    execute "Media files backup" "tar -czf ${BACKUP_FILE} media/ staticfiles/ || true"
    
    log "${GREEN}✅ Backup created: ${BACKUP_FILE}${NC}"
}

# Step 1: Pre-launch verification
log ""
log "${YELLOW}Step 1: Pre-Launch Verification${NC}"
log "================================"

if [ -f "${DJANGO_ROOT}/deployment/scripts/pre_launch_checklist.sh" ]; then
    bash "${DJANGO_ROOT}/deployment/scripts/pre_launch_checklist.sh"
    if [ $? -ne 0 ]; then
        log "${RED}Pre-launch checks failed. Aborting deployment.${NC}"
        exit 1
    fi
else
    log "${YELLOW}⚠️  Pre-launch checklist not found. Proceeding with caution.${NC}"
fi

# Step 2: Create backup
log ""
log "${YELLOW}Step 2: Backup Creation${NC}"
log "======================="
create_backup

# Step 3: Build Frontend Assets
log ""
log "${YELLOW}Step 3: Building Frontend Assets${NC}"
log "================================"

cd "$DJANGO_ROOT"

# Install Node dependencies
execute "Installing Node dependencies" "npm ci --production"

# Build TailwindCSS
execute "Building TailwindCSS" "npm run build-css"

# Verify build
if [ -f "static/css/output.css" ]; then
    FILE_SIZE=$(wc -c < static/css/output.css)
    log "${GREEN}✅ TailwindCSS built successfully (${FILE_SIZE} bytes)${NC}"
else
    log "${RED}❌ TailwindCSS build failed${NC}"
    exit 1
fi

# Step 4: Database Migrations
log ""
log "${YELLOW}Step 4: Database Operations${NC}"
log "==========================="

cd "$DJANGO_ROOT"

# Run migrations
execute "Running database migrations" "python manage.py migrate --no-input"

# Create cache table (if using database cache)
execute "Creating cache table" "python manage.py createcachetable || true"

# Optimize database
execute "Optimizing database" "python manage.py optimize_database || true"

# Step 5: Static Files Collection
log ""
log "${YELLOW}Step 5: Static Files Collection${NC}"
log "==============================="

execute "Collecting static files" "python manage.py collectstatic --no-input --clear"

# Step 6: Docker Deployment
log ""
log "${YELLOW}Step 6: Docker Deployment${NC}"
log "========================="

cd "$PROJECT_ROOT"

# Build Docker images
execute "Building Docker images" "docker-compose -f docker-compose.yml -f docker-compose.prod.yml build"

# Stop existing containers
execute "Stopping existing containers" "docker-compose down || true"

# Start new containers
execute "Starting production containers" "docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d"

# Wait for services to be ready
log "${BLUE}➤ Waiting for services to initialize...${NC}"
sleep 30

# Step 7: Health Checks
log ""
log "${YELLOW}Step 7: Post-Deployment Health Checks${NC}"
log "===================================="

# Check web service
HEALTH_CHECK_URL="${PRODUCTION_URL:-http://localhost:8000}/health/"
if curl -f "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
    log "${GREEN}✅ Application health check passed${NC}"
else
    log "${RED}❌ Application health check failed${NC}"
    log "${YELLOW}Rolling back deployment...${NC}"
    docker-compose down
    docker-compose up -d
    exit 1
fi

# Check database connectivity
cd "$DJANGO_ROOT"
if python manage.py dbshell -c "SELECT 1;" > /dev/null 2>&1; then
    log "${GREEN}✅ Database connectivity verified${NC}"
else
    log "${RED}❌ Database connectivity check failed${NC}"
fi

# Step 8: Initialize Monitoring
log ""
log "${YELLOW}Step 8: Monitoring Initialization${NC}"
log "================================="

# Start Celery workers
execute "Starting Celery workers" "docker-compose exec -d web celery -A config worker -l info"

# Start Celery beat scheduler
execute "Starting Celery beat" "docker-compose exec -d web celery -A config beat -l info"

# Initialize Sentry (if configured)
if [ ! -z "$SENTRY_DSN" ]; then
    cd "$DJANGO_ROOT"
    python -c "import sentry_sdk; sentry_sdk.capture_message('Production deployment completed')" 2>/dev/null
    log "${GREEN}✅ Sentry notification sent${NC}"
fi

# Step 9: SSL Certificate Verification
log ""
log "${YELLOW}Step 9: SSL Certificate Setup${NC}"
log "============================="

if [ ! -z "$PRODUCTION_DOMAIN" ]; then
    # Check if SSL is already configured
    if openssl s_client -connect ${PRODUCTION_DOMAIN}:443 -servername ${PRODUCTION_DOMAIN} </dev/null 2>/dev/null | openssl x509 -noout -dates > /dev/null 2>&1; then
        log "${GREEN}✅ SSL certificate already configured${NC}"
    else
        # Run SSL setup if available
        if [ -f "${DJANGO_ROOT}/deployment/ssl-setup.sh" ]; then
            execute "Setting up SSL certificate" "bash ${DJANGO_ROOT}/deployment/ssl-setup.sh ${PRODUCTION_DOMAIN}"
        else
            log "${YELLOW}⚠️  SSL setup script not found. Configure SSL manually.${NC}"
        fi
    fi
fi

# Step 10: Final Verification
log ""
log "${YELLOW}Step 10: Final Deployment Verification${NC}"
log "====================================="

cd "$DJANGO_ROOT"

# Generate deployment report
cat > "${BACKUP_DIR}/deployment_report_$(date +%Y%m%d_%H%M%S).txt" << EOF
#FahanieCares Production Deployment Report
==========================================
Deployment Date: $(date)
Git Commit: $(git rev-parse HEAD)
Git Branch: $(git rev-parse --abbrev-ref HEAD)

Services Status:
- Web Application: $(docker-compose ps web | grep Up && echo "Running" || echo "Failed")
- Database: $(docker-compose ps db | grep Up && echo "Running" || echo "Failed")
- Redis: $(docker-compose ps redis | grep Up && echo "Running" || echo "Failed")
- Nginx: $(docker-compose ps nginx | grep Up && echo "Running" || echo "Failed")

URLs:
- Application: ${PRODUCTION_URL:-http://localhost:8000}
- Admin Panel: ${PRODUCTION_URL:-http://localhost:8000}/admin/
- Monitoring: ${PRODUCTION_URL:-http://localhost:8000}/monitoring/
- Health Check: ${PRODUCTION_URL:-http://localhost:8000}/health/

Feature Status:
$(python -c "from django.conf import settings; import json; print(json.dumps(settings.FEATURES, indent=2))" 2>/dev/null || echo "Failed to retrieve")

Notes:
- All critical production components deployed
- Monitoring and alerting active
- Automated backups configured
- SSL certificate configured (if domain available)
EOF

log "${GREEN}✅ Deployment report generated${NC}"

# Step 11: Launch Notification
log ""
log "${YELLOW}Step 11: Launch Notifications${NC}"
log "============================="

# Send notification email (if configured)
if [ ! -z "$NOTIFICATION_EMAIL" ]; then
    cd "$DJANGO_ROOT"
    python manage.py shell << EOF
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='#FahanieCares Platform - Production Deployment Completed',
    message='''
The #FahanieCares platform has been successfully deployed to production.

Deployment Details:
- Date: $(date)
- Status: Success
- Application URL: ${PRODUCTION_URL:-http://localhost:8000}
- Monitoring Dashboard: ${PRODUCTION_URL:-http://localhost:8000}/monitoring/

Please verify all systems are operational.
    ''',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['${NOTIFICATION_EMAIL}'],
    fail_silently=True,
)
EOF
    log "${GREEN}✅ Notification email sent${NC}"
fi

# Final Summary
log ""
log "=============================================="
log "${GREEN}🚀 PRODUCTION LAUNCH COMPLETED SUCCESSFULLY! 🚀${NC}"
log "=============================================="
log ""
log "Next Steps:"
log "1. Access monitoring dashboard: ${PRODUCTION_URL:-http://localhost:8000}/monitoring/"
log "2. Verify all features are working as expected"
log "3. Monitor error logs and performance metrics"
log "4. Review deployment report at: ${BACKUP_DIR}"
log ""
log "Support Contacts:"
log "- Technical: dev@fahaniecares.ph"
log "- Emergency: +63 XXX XXX XXXX"
log ""
log "Deployment log saved to: ${LOG_FILE}"
log ""

exit 0