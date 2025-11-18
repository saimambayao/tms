#!/bin/bash
# Daily Operations Checklist for #FahanieCares Platform
# Run this script daily to ensure system health and performance

set -e

echo "=== #FahanieCares Daily Operations Check ==="
echo "Date: $(date)"
echo "==========================================="

# Configuration
DJANGO_ROOT="/Users/macbookpro/Documents/fahanie-cares/src"
LOG_DIR="${LOG_DIR:-${DJANGO_ROOT}/logs}"
REPORT_DIR="${REPORT_DIR:-${LOG_DIR}/daily_reports}"
REPORT_FILE="${REPORT_DIR}/daily_report_$(date +%Y%m%d).txt"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure directories exist
mkdir -p "$REPORT_DIR"
mkdir -p "$LOG_DIR"

# Function to log to report
report() {
    echo "$1" | tee -a "$REPORT_FILE"
}

# Function to check status
check_status() {
    if [ $? -eq 0 ]; then
        report "✅ $1"
        return 0
    else
        report "❌ $1"
        return 1
    fi
}

# Initialize report
cat > "$REPORT_FILE" << EOF
#FahanieCares Daily Operations Report
=====================================
Date: $(date)
Server: $(hostname)

EOF

# 1. System Health Check
report ""
report "1. SYSTEM HEALTH CHECK"
report "----------------------"

cd "$DJANGO_ROOT"

# Check application health
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    HEALTH_DATA=$(curl -s http://localhost:8000/health/)
    report "✅ Application health check: PASSED"
    report "   Response: ${HEALTH_DATA}"
else
    report "❌ Application health check: FAILED"
fi

# Check Docker containers
report ""
report "Docker Container Status:"
docker-compose ps >> "$REPORT_FILE" 2>&1

# System resources
report ""
report "System Resources:"
report "- CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
report "- Memory Usage: $(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')"
report "- Disk Usage: $(df -h / | awk 'NR==2{print $5}')"

# 2. Error Log Review
report ""
report "2. ERROR LOG ANALYSIS"
report "--------------------"

# Check Django error logs
ERROR_COUNT=0
if [ -f "${LOG_DIR}/errors.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR" "${LOG_DIR}/errors.log" 2>/dev/null || echo "0")
    CRITICAL_COUNT=$(grep -c "CRITICAL" "${LOG_DIR}/errors.log" 2>/dev/null || echo "0")
    
    report "Errors in last 24 hours:"
    report "- ERROR level: ${ERROR_COUNT}"
    report "- CRITICAL level: ${CRITICAL_COUNT}"
    
    if [ $CRITICAL_COUNT -gt 0 ]; then
        report ""
        report "⚠️  CRITICAL ERRORS FOUND - Recent samples:"
        tail -n 20 "${LOG_DIR}/errors.log" | grep "CRITICAL" | head -5 >> "$REPORT_FILE"
    fi
else
    report "⚠️  Error log file not found"
fi

# Check Nginx access logs
if [ -f "/var/log/nginx/access.log" ]; then
    REQUEST_COUNT=$(wc -l < /var/log/nginx/access.log)
    ERROR_RESPONSES=$(grep -E "\" [4-5][0-9]{2} " /var/log/nginx/access.log | wc -l)
    
    report ""
    report "Web Traffic Statistics:"
    report "- Total requests: ${REQUEST_COUNT}"
    report "- Error responses (4xx/5xx): ${ERROR_RESPONSES}"
fi

# 3. Performance Metrics
report ""
report "3. PERFORMANCE METRICS"
report "---------------------"

# Database performance
python manage.py dbshell << EOF > /tmp/db_stats.txt 2>&1
SELECT 
    'Active connections' as metric,
    count(*) as value
FROM pg_stat_activity
WHERE state = 'active'
UNION ALL
SELECT 
    'Total connections',
    count(*)
FROM pg_stat_activity
UNION ALL
SELECT
    'Longest running query (seconds)',
    COALESCE(EXTRACT(epoch FROM max(now() - query_start)), 0)::int
FROM pg_stat_activity
WHERE state = 'active' AND query_start IS NOT NULL;
EOF

if [ -f "/tmp/db_stats.txt" ]; then
    report "Database Statistics:"
    cat /tmp/db_stats.txt >> "$REPORT_FILE"
    rm /tmp/db_stats.txt
fi

# Cache performance (Redis)
if command -v redis-cli &> /dev/null; then
    REDIS_INFO=$(redis-cli INFO stats | grep -E "(keyspace_hits|keyspace_misses|connected_clients)")
    report ""
    report "Redis Cache Statistics:"
    echo "$REDIS_INFO" >> "$REPORT_FILE"
fi

# 4. Backup Status
report ""
report "4. BACKUP STATUS"
report "----------------"

BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares}"
if [ -d "$BACKUP_DIR" ]; then
    LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime -1 | sort -r | head -1)
    if [ ! -z "$LATEST_BACKUP" ]; then
        BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
        report "✅ Latest backup: $(basename $LATEST_BACKUP)"
        report "   Size: ${BACKUP_SIZE}"
        report "   Age: Less than 24 hours"
    else
        report "⚠️  No backup found in last 24 hours"
    fi
else
    report "❌ Backup directory not found"
fi

# 5. SSL Certificate Check
report ""
report "5. SSL CERTIFICATE STATUS"
report "------------------------"

if [ ! -z "$PRODUCTION_DOMAIN" ]; then
    SSL_EXPIRY=$(echo | openssl s_client -servername ${PRODUCTION_DOMAIN} -connect ${PRODUCTION_DOMAIN}:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ ! -z "$SSL_EXPIRY" ]; then
        EXPIRY_EPOCH=$(date -d "$SSL_EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$SSL_EXPIRY" +%s 2>/dev/null)
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
        
        if [ $DAYS_LEFT -lt 30 ]; then
            report "⚠️  SSL certificate expires in ${DAYS_LEFT} days!"
        else
            report "✅ SSL certificate valid for ${DAYS_LEFT} days"
        fi
        report "   Expires: ${SSL_EXPIRY}"
    else
        report "⚠️  Unable to check SSL certificate"
    fi
else
    report "- SSL check skipped (no domain configured)"
fi

# 6. Security Scan
report ""
report "6. SECURITY QUICK CHECK"
report "----------------------"

# Check for failed login attempts
if [ -f "${LOG_DIR}/security.log" ]; then
    FAILED_LOGINS=$(grep -c "Failed login" "${LOG_DIR}/security.log" 2>/dev/null || echo "0")
    BLOCKED_IPS=$(grep -c "IP blocked" "${LOG_DIR}/security.log" 2>/dev/null || echo "0")
    
    report "Security Events (last 24h):"
    report "- Failed login attempts: ${FAILED_LOGINS}"
    report "- Blocked IP addresses: ${BLOCKED_IPS}"
    
    if [ $FAILED_LOGINS -gt 100 ]; then
        report "⚠️  High number of failed login attempts detected"
    fi
fi

# Check file permissions
report ""
report "File Permission Check:"
PERMISSION_ISSUES=0

# Check secret files
if [ -f "${DJANGO_ROOT}/.env" ]; then
    PERM=$(stat -c %a "${DJANGO_ROOT}/.env" 2>/dev/null || stat -f %p "${DJANGO_ROOT}/.env" 2>/dev/null)
    if [[ ! "$PERM" =~ 600$ ]]; then
        report "⚠️  .env file has loose permissions: ${PERM}"
        ((PERMISSION_ISSUES++))
    fi
fi

if [ $PERMISSION_ISSUES -eq 0 ]; then
    report "✅ File permissions secure"
fi

# 7. Database Maintenance
report ""
report "7. DATABASE MAINTENANCE"
report "----------------------"

# Vacuum and analyze status
python manage.py dbshell << EOF > /tmp/db_maint.txt 2>&1
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY greatest(
    COALESCE(last_vacuum, '1900-01-01'::timestamp),
    COALESCE(last_autovacuum, '1900-01-01'::timestamp)
)
LIMIT 5;
EOF

if [ -f "/tmp/db_maint.txt" ]; then
    report "Tables requiring maintenance:"
    cat /tmp/db_maint.txt >> "$REPORT_FILE"
    rm /tmp/db_maint.txt
fi

# 8. Application Metrics
report ""
report "8. APPLICATION METRICS"
report "---------------------"

cd "$DJANGO_ROOT"

# User activity
python manage.py shell << EOF > /tmp/app_stats.txt 2>&1
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
now = timezone.now()
day_ago = now - timedelta(days=1)

total_users = User.objects.count()
active_today = User.objects.filter(last_login__gte=day_ago).count()
new_users = User.objects.filter(date_joined__gte=day_ago).count()

print(f"Total users: {total_users}")
print(f"Active in last 24h: {active_today}")
print(f"New registrations: {new_users}")

# Feature usage
from apps.chapters.models import Chapter
from apps.services.models import MinistryProgram

print(f"Active chapters: {Chapter.objects.filter(status='active').count()}")
print(f"Ministry programs: {MinistryProgram.objects.filter(is_active=True).count()}")
EOF

if [ -f "/tmp/app_stats.txt" ]; then
    report "Application Statistics:"
    cat /tmp/app_stats.txt >> "$REPORT_FILE"
    rm /tmp/app_stats.txt
fi

# 9. Scheduled Tasks
report ""
report "9. SCHEDULED TASKS"
report "------------------"

# Check Celery workers
CELERY_STATUS=$(docker-compose exec web celery -A config inspect active 2>&1 | head -10)
if [[ "$CELERY_STATUS" == *"Error"* ]]; then
    report "❌ Celery workers not responding"
else
    report "✅ Celery workers active"
fi

# Check last task execution
python manage.py shell << EOF >> "$REPORT_FILE" 2>&1
from django_celery_results.models import TaskResult
from django.utils import timezone
from datetime import timedelta

recent_tasks = TaskResult.objects.filter(
    date_created__gte=timezone.now() - timedelta(days=1)
).count()

failed_tasks = TaskResult.objects.filter(
    date_created__gte=timezone.now() - timedelta(days=1),
    status='FAILURE'
).count()

print(f"Tasks executed (24h): {recent_tasks}")
print(f"Failed tasks: {failed_tasks}")
EOF

# 10. Recommendations
report ""
report "10. RECOMMENDATIONS"
report "-------------------"

# Generate recommendations based on findings
RECOMMENDATIONS=()

if [ $ERROR_COUNT -gt 100 ]; then
    RECOMMENDATIONS+=("- Investigate high error rate in application logs")
fi

if [ $CRITICAL_COUNT -gt 0 ]; then
    RECOMMENDATIONS+=("- URGENT: Address critical errors immediately")
fi

if [ "$DAYS_LEFT" -lt 30 ] 2>/dev/null; then
    RECOMMENDATIONS+=("- Renew SSL certificate before expiration")
fi

if [ ${#RECOMMENDATIONS[@]} -eq 0 ]; then
    report "✅ No immediate actions required"
else
    report "Action items:"
    for rec in "${RECOMMENDATIONS[@]}"; do
        report "$rec"
    done
fi

# Summary
report ""
report "======================================"
report "DAILY OPERATIONS SUMMARY"
report "======================================"
report "Report generated: $(date)"
report "Report location: ${REPORT_FILE}"
report ""

# Email report (if configured)
if [ ! -z "$DAILY_REPORT_EMAIL" ]; then
    cd "$DJANGO_ROOT"
    python manage.py shell << EOF
from django.core.mail import EmailMessage
from django.conf import settings

with open('${REPORT_FILE}', 'r') as f:
    report_content = f.read()

email = EmailMessage(
    subject=f'#FahanieCares Daily Operations Report - {timezone.now().strftime("%Y-%m-%d")}',
    body=report_content,
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['${DAILY_REPORT_EMAIL}'],
)
email.send(fail_silently=True)
EOF
    echo "Report emailed to: ${DAILY_REPORT_EMAIL}"
fi

echo -e "${GREEN}Daily operations check completed!${NC}"
echo "Full report saved to: ${REPORT_FILE}"

# Exit with error if critical issues found
if [ $CRITICAL_COUNT -gt 0 ] 2>/dev/null; then
    exit 1
else
    exit 0
fi