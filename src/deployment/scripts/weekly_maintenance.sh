#!/bin/bash
# Weekly Maintenance Script for #FahanieCares Platform
# Run this script weekly (preferably during low-traffic hours)

set -e

echo "=== #FahanieCares Weekly Maintenance ==="
echo "Starting at: $(date)"
echo "========================================"

# Configuration
DJANGO_ROOT="/Users/macbookpro/Documents/fahanie-cares/src"
LOG_DIR="${LOG_DIR:-${DJANGO_ROOT}/logs}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares}"
MAINTENANCE_LOG="${LOG_DIR}/maintenance/weekly_$(date +%Y%m%d_%H%M%S).log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure directories exist
mkdir -p "$(dirname "$MAINTENANCE_LOG")"
mkdir -p "$BACKUP_DIR/weekly"

# Function to log
log() {
    echo -e "$1" | tee -a "$MAINTENANCE_LOG"
}

# Function to execute with logging
execute() {
    local description="$1"
    local command="$2"
    
    log "${BLUE}➤ ${description}...${NC}"
    
    if eval "$command" >> "$MAINTENANCE_LOG" 2>&1; then
        log "${GREEN}✅ ${description} completed${NC}"
        return 0
    else
        log "${RED}❌ ${description} failed${NC}"
        return 1
    fi
}

# 1. Database Maintenance
log ""
log "${YELLOW}1. DATABASE MAINTENANCE${NC}"
log "========================"

cd "$DJANGO_ROOT"

# Full database backup before maintenance
log "Creating pre-maintenance backup..."
BACKUP_FILE="${BACKUP_DIR}/weekly/db_pre_maintenance_$(date +%Y%m%d_%H%M%S).sql"
if [ ! -z "$DATABASE_URL" ]; then
    execute "Database backup" "pg_dump $DATABASE_URL > $BACKUP_FILE"
    execute "Compressing backup" "gzip $BACKUP_FILE"
fi

# Vacuum and analyze all tables
log "Running VACUUM and ANALYZE..."
python manage.py dbshell << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
-- Vacuum and analyze all user tables
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT schemaname, tablename 
        FROM pg_stat_user_tables 
        WHERE schemaname = 'public'
    LOOP
        RAISE NOTICE 'Vacuuming %.%', r.schemaname, r.tablename;
        EXECUTE format('VACUUM ANALYZE %I.%I', r.schemaname, r.tablename);
    END LOOP;
END $$;

-- Update table statistics
ANALYZE;

-- Show database size
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = current_database();
EOF

# Clean old sessions
execute "Cleaning expired sessions" "python manage.py clearsessions"

# Clean old admin log entries (keep 90 days)
python manage.py shell << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
from django.contrib.admin.models import LogEntry
from django.utils import timezone
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=90)
deleted = LogEntry.objects.filter(action_time__lt=cutoff_date).delete()
print(f"Deleted {deleted[0]} old admin log entries")
EOF

# 2. File System Cleanup
log ""
log "${YELLOW}2. FILE SYSTEM CLEANUP${NC}"
log "======================="

# Clean old log files
log "Cleaning old log files..."
find "$LOG_DIR" -name "*.log" -mtime +30 -type f -exec gzip {} \; 2>/dev/null || true
find "$LOG_DIR" -name "*.gz" -mtime +90 -type f -delete 2>/dev/null || true

# Clean temporary files
TEMP_DIRS=(
    "/tmp/fahaniecares_*"
    "${DJANGO_ROOT}/media/temp/*"
    "${DJANGO_ROOT}/staticfiles/CACHE/*"
)

for dir in "${TEMP_DIRS[@]}"; do
    if ls $dir 2>/dev/null | grep -q .; then
        execute "Cleaning $dir" "find $dir -mtime +7 -delete 2>/dev/null || true"
    fi
done

# Clean old backups (keep last 4 weekly backups)
log "Managing backup retention..."
if [ -d "$BACKUP_DIR/weekly" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR/weekly" | wc -l)
    if [ $BACKUP_COUNT -gt 4 ]; then
        TO_DELETE=$((BACKUP_COUNT - 4))
        ls -1t "$BACKUP_DIR/weekly" | tail -n $TO_DELETE | while read backup; do
            execute "Removing old backup $backup" "rm -f $BACKUP_DIR/weekly/$backup"
        done
    fi
fi

# 3. Cache Optimization
log ""
log "${YELLOW}3. CACHE OPTIMIZATION${NC}"
log "====================="

# Clear Django cache
execute "Clearing Django cache" "python manage.py shell -c 'from django.core.cache import cache; cache.clear()'"

# Clear Redis cache if available
if command -v redis-cli &> /dev/null; then
    log "Redis cache statistics before clearing:"
    redis-cli INFO stats | grep -E "(used_memory|expired_keys|evicted_keys)" >> "$MAINTENANCE_LOG"
    
    execute "Flushing Redis cache" "redis-cli FLUSHDB"
    
    # Warm up cache with frequently accessed data
    execute "Warming up cache" "python manage.py warm_cache 2>/dev/null || true"
fi

# 4. Security Audit
log ""
log "${YELLOW}4. SECURITY AUDIT${NC}"
log "=================="

# Check for security updates
log "Checking for security updates..."
pip list --outdated --format=json > /tmp/outdated_packages.json

python << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
import json

with open('/tmp/outdated_packages.json', 'r') as f:
    outdated = json.load(f)

security_packages = ['django', 'djangorestframework', 'gunicorn', 'psycopg2', 'redis', 'celery']
security_updates = [pkg for pkg in outdated if pkg['name'].lower() in security_packages]

if security_updates:
    print("⚠️  Security updates available:")
    for pkg in security_updates:
        print(f"  - {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")
else:
    print("✅ All security-critical packages up to date")
EOF

# Check for weak passwords
python manage.py shell << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

# Check for users who haven't changed password in 90 days
old_password_users = User.objects.filter(
    password_changed__lt=timezone.now() - timedelta(days=90)
).count()

if old_password_users > 0:
    print(f"⚠️  {old_password_users} users haven't changed password in 90+ days")

# Check for users without MFA
if hasattr(User, 'mfa_enabled'):
    no_mfa_users = User.objects.filter(
        is_staff=True,
        mfa_enabled=False
    ).count()
    if no_mfa_users > 0:
        print(f"⚠️  {no_mfa_users} staff users don't have MFA enabled")
EOF

# File permission audit
log "Checking file permissions..."
PERMISSION_ISSUES=0

# Check sensitive files
SENSITIVE_FILES=(
    "${DJANGO_ROOT}/.env"
    "${DJANGO_ROOT}/config/settings/production.py"
    "$BACKUP_DIR"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -e "$file" ]; then
        PERM=$(stat -c %a "$file" 2>/dev/null || stat -f %p "$file" 2>/dev/null | tail -c 4)
        if [[ ! "$PERM" =~ ^[67]00$ ]] && [[ ! "$PERM" =~ ^[67]50$ ]]; then
            log "⚠️  Insecure permissions on $file: $PERM"
            ((PERMISSION_ISSUES++))
        fi
    fi
done

if [ $PERMISSION_ISSUES -eq 0 ]; then
    log "✅ File permissions audit passed"
fi

# 5. Performance Optimization
log ""
log "${YELLOW}5. PERFORMANCE OPTIMIZATION${NC}"
log "==========================="

# Rebuild search indexes (if using)
execute "Rebuilding search indexes" "python manage.py rebuild_index --noinput 2>/dev/null || true"

# Update database statistics
python manage.py dbshell << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
-- Update query planner statistics
ANALYZE;

-- Show slow queries
SELECT 
    calls,
    total_time,
    mean_time,
    query
FROM pg_stat_statements
WHERE mean_time > 1000  -- queries taking more than 1 second
ORDER BY mean_time DESC
LIMIT 10;
EOF

# Check and rebuild database indexes
python manage.py dbshell << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
-- Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public'
ORDER BY tablename, indexname;

-- Rebuild fragmented indexes
REINDEX DATABASE CONCURRENTLY current_database();
EOF

# 6. Data Archival
log ""
log "${YELLOW}6. DATA ARCHIVAL${NC}"
log "================="

# Archive old referrals (if enabled)
python manage.py shell << 'EOF' >> "$MAINTENANCE_LOG" 2>&1
from apps.referrals.models import Referral
from django.utils import timezone
from datetime import timedelta

# Count old completed referrals
archive_date = timezone.now() - timedelta(days=365)
old_referrals = Referral.objects.filter(
    status='completed',
    updated_at__lt=archive_date
).count()

if old_referrals > 0:
    print(f"Found {old_referrals} referrals ready for archival")
    # Archival would be implemented based on business rules
EOF

# 7. SSL Certificate Check
log ""
log "${YELLOW}7. SSL CERTIFICATE MAINTENANCE${NC}"
log "=============================="

if [ ! -z "$PRODUCTION_DOMAIN" ]; then
    # Check certificate expiration
    CERT_CHECK=$(echo | openssl s_client -servername ${PRODUCTION_DOMAIN} -connect ${PRODUCTION_DOMAIN}:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    log "SSL Certificate Status:"
    echo "$CERT_CHECK" >> "$MAINTENANCE_LOG"
    
    # Auto-renew if using Let's Encrypt
    if command -v certbot &> /dev/null; then
        execute "Checking SSL auto-renewal" "certbot renew --dry-run"
    fi
fi

# 8. Docker Maintenance
log ""
log "${YELLOW}8. DOCKER MAINTENANCE${NC}"
log "====================="

# Clean unused Docker resources
execute "Cleaning Docker system" "docker system prune -f"

# Remove old images
execute "Removing old Docker images" "docker image prune -a -f --filter 'until=168h'"

# Check Docker health
docker system df >> "$MAINTENANCE_LOG"

# 9. Monitoring Integration Check
log ""
log "${YELLOW}9. MONITORING VERIFICATION${NC}"
log "=========================="

# Test Sentry integration
if [ ! -z "$SENTRY_DSN" ]; then
    cd "$DJANGO_ROOT"
    python -c "import sentry_sdk; sentry_sdk.capture_message('Weekly maintenance completed')" 2>/dev/null
    log "✅ Sentry test message sent"
fi

# Verify monitoring endpoints
ENDPOINTS=(
    "http://localhost:8000/health/"
    "http://localhost:8000/metrics/"
    "http://localhost:8000/monitoring/"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -f "$endpoint" > /dev/null 2>&1; then
        log "✅ Monitoring endpoint available: $endpoint"
    else
        log "❌ Monitoring endpoint failed: $endpoint"
    fi
done

# 10. Generate Maintenance Report
log ""
log "${YELLOW}10. MAINTENANCE SUMMARY${NC}"
log "======================="

REPORT_FILE="${LOG_DIR}/maintenance/weekly_report_$(date +%Y%m%d).txt"

cat > "$REPORT_FILE" << EOF
#FahanieCares Weekly Maintenance Report
======================================
Date: $(date)
Duration: $SECONDS seconds

Tasks Completed:
- Database maintenance (VACUUM, ANALYZE, REINDEX)
- File system cleanup
- Cache optimization
- Security audit
- Performance optimization
- Data archival check
- SSL certificate verification
- Docker maintenance
- Monitoring verification

Next Maintenance: $(date -d "+7 days" 2>/dev/null || date -v +7d)

Log Location: $MAINTENANCE_LOG
EOF

# Email report
if [ ! -z "$MAINTENANCE_EMAIL" ]; then
    cd "$DJANGO_ROOT"
    python manage.py shell << EOF
from django.core.mail import EmailMessage
from django.conf import settings

with open('${REPORT_FILE}', 'r') as f:
    report_content = f.read()

with open('${MAINTENANCE_LOG}', 'r') as f:
    log_content = f.read()

email = EmailMessage(
    subject=f'#FahanieCares Weekly Maintenance Report - {timezone.now().strftime("%Y-%m-%d")}',
    body=report_content + "\n\n--- Detailed Log ---\n\n" + log_content[-5000:],  # Last 5000 chars
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['${MAINTENANCE_EMAIL}'],
)
email.send(fail_silently=True)
EOF
    log "Report emailed to: ${MAINTENANCE_EMAIL}"
fi

log ""
log "========================================"
log "${GREEN}✅ WEEKLY MAINTENANCE COMPLETED${NC}"
log "========================================"
log "Total duration: $SECONDS seconds"
log "Report saved to: $REPORT_FILE"
log "Detailed log: $MAINTENANCE_LOG"
log ""

exit 0