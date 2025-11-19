# BM Parliament System Monitoring Guide

## Overview

This guide outlines procedures for monitoring the BM Parliament website to ensure optimal performance, security, and availability.

## Monitoring Components

### 1. Infrastructure Monitoring

#### Server Health
- **CPU Usage**: Alert if >80% for 5 minutes
- **Memory Usage**: Alert if >85%
- **Disk Space**: Alert if <10% free
- **Network Traffic**: Monitor for anomalies

#### Application Performance
- **Response Time**: Alert if >2 seconds
- **Error Rate**: Alert if >1% of requests
- **Database Queries**: Alert if >1 second
- **API Calls**: Monitor rate limits

### 2. Application Monitoring

#### Key Metrics
- Active users
- Request volume
- Error logs
- Transaction success rate
- Session duration

#### Health Checks
```python
# health_check.py
def health_check():
    checks = {
        'database': check_database(),
        'notion_api': check_notion_api(),
        'cache': check_cache(),
        'storage': check_storage(),
        'email': check_email_service()
    }
    return all(checks.values())
```

### 3. Security Monitoring

#### Security Events
- Failed login attempts
- Unauthorized access attempts
- File upload anomalies
- SQL injection attempts
- XSS attempts

#### Audit Logs
- User actions
- System changes
- Data exports
- Permission changes

## Monitoring Tools

### 1. System Monitoring
```bash
# CPU and Memory
top
htop
vmstat 1

# Disk Usage
df -h
du -sh /var/www/bm-parliament/*

# Network
netstat -tuln
iftop
```

### 2. Application Monitoring
```bash
# Django Logs
tail -f /var/log/bm-parliament/django.log

# Nginx Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Database Logs
tail -f /var/log/postgresql/postgresql.log
```

### 3. Automated Monitoring Script
```bash
#!/bin/bash
# monitor.sh

# Check system resources
check_resources() {
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
    DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    if [ $(echo "$CPU > 80" | bc) -eq 1 ]; then
        alert "High CPU usage: $CPU%"
    fi
    
    if [ $(echo "$MEM > 85" | bc) -eq 1 ]; then
        alert "High memory usage: $MEM%"
    fi
    
    if [ $DISK -gt 90 ]; then
        alert "Low disk space: $DISK% used"
    fi
}

# Check application
check_application() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/)
    if [ $response -ne 200 ]; then
        alert "Application health check failed: HTTP $response"
    fi
}

# Send alert
alert() {
    echo "[$(date)] ALERT: $1" >> /var/log/bm-parliament/alerts.log
    # Send email or SMS alert
    echo "$1" | mail -s "BM Parliament Alert" admin@bm-parliament.gov.ph
}

# Run checks
while true; do
    check_resources
    check_application
    sleep 300  # Check every 5 minutes
done
```

## Alert Configuration

### Priority Levels

#### Critical (P1)
- System down
- Database unreachable
- Security breach
- Data loss

**Response Time**: Immediate (within 15 minutes)

#### High (P2)
- Performance degradation
- Service errors
- Failed backups
- High resource usage

**Response Time**: Within 1 hour

#### Medium (P3)
- Warning conditions
- Non-critical errors
- Scheduled maintenance

**Response Time**: Within 4 hours

#### Low (P4)
- Information logs
- Routine checks
- Performance metrics

**Response Time**: Next business day

### Alert Channels

1. **Email Alerts**
   - Critical: All team members
   - High: System administrators
   - Medium: Support team
   - Low: Log file only

2. **SMS Alerts**
   - Critical only
   - On-call personnel

3. **Dashboard**
   - Real-time status
   - Historical trends
   - Alert history

## Incident Response

### Response Procedure

1. **Detection**
   - Automated alert received
   - User report
   - Routine check

2. **Assessment**
   - Verify the issue
   - Determine severity
   - Check impact scope

3. **Response**
   - Follow runbook
   - Implement fix
   - Monitor results

4. **Communication**
   - Update status page
   - Notify stakeholders
   - Log actions taken

5. **Resolution**
   - Verify fix
   - Document solution
   - Update procedures

6. **Review**
   - Post-mortem analysis
   - Update documentation
   - Improve monitoring

### Common Issues and Solutions

#### High CPU Usage
1. Check running processes
2. Identify resource-heavy queries
3. Restart application if needed
4. Scale resources if persistent

#### Database Connection Issues
1. Check database status
2. Verify connection settings
3. Check connection pool
4. Restart database if needed

#### API Rate Limiting
1. Check API usage
2. Implement caching
3. Optimize API calls
4. Request limit increase

## Performance Optimization

### Database Optimization
```sql
-- Find slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

### Cache Optimization
```python
# Check cache performance
from django.core.cache import cache
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Test cache
        cache.set('test_key', 'test_value', 300)
        value = cache.get('test_key')
        
        # Check cache stats
        stats = cache._cache.get_stats()
        self.stdout.write(f"Cache hits: {stats['hits']}")
        self.stdout.write(f"Cache misses: {stats['misses']}")
```

## Backup Monitoring

### Backup Verification
```bash
#!/bin/bash
# verify_backup.sh

BACKUP_DIR="/var/backups/bm-parliament"
TODAY=$(date +%Y%m%d)

# Check if today's backup exists
if [ -f "$BACKUP_DIR/backup_$TODAY.tar.gz" ]; then
    # Verify backup integrity
    tar -tzf "$BACKUP_DIR/backup_$TODAY.tar.gz" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "Backup verified successfully"
    else
        alert "Backup verification failed"
    fi
else
    alert "No backup found for today"
fi
```

## Reporting

### Daily Report
- System uptime
- Performance metrics
- Error summary
- User activity
- Resource usage

### Weekly Report
- Trend analysis
- Incident summary
- Capacity planning
- Security events
- Backup status

### Monthly Report
- SLA compliance
- Performance trends
- Capacity forecast
- Security audit
- Improvement recommendations

## Maintenance Windows

### Scheduled Maintenance
- **Time**: Sundays, 2-4 AM
- **Frequency**: Monthly
- **Duration**: 2 hours maximum

### Emergency Maintenance
- Notify users immediately
- Minimize downtime
- Document all changes
- Post-maintenance verification

---

*Last Updated: [Current Date]*  
*Next Review: [Date + 3 months]*