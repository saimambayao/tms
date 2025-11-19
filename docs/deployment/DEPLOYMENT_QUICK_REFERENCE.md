# ORM Field Rename Migration - Quick Reference Guide

**Migration:** `unified_db.0002` + `constituents.0023`
**Target:** Rename `fahanie_cares_member` → `bm_parliament_member`
**Estimated Duration:** < 500ms database lock, ~60s total deployment
**Recommended Strategy:** Blue-Green Deployment
**Risk Level:** LOW (with proper execution)

---

## Pre-Deployment Checklist

```bash
# 1. Backup database
docker exec bmparliament_db pg_dump -U bmparliament_user bmparliament_prod | \
  gzip > backups/pre_migration_$(date +%Y%m%d_%H%M%S).sql.gz

# 2. Verify production health
curl https://bmparliament.gov.ph/health/detailed/ | jq '.'

# 3. Clear caches
docker exec bmparliament_redis redis-cli -a $REDIS_PASSWORD \
  EVAL "return redis.call('del', unpack(redis.call('keys', 'bmparliament:views*')))" 0

# 4. Build new image
docker-compose build web
```

## Deployment Command

```bash
# Blue-Green deployment (RECOMMENDED - zero downtime)
docker-compose up -d --no-deps --scale web=2 web

# Wait for health checks
timeout 120 bash -c 'until curl -s https://bmparliament.gov.ph/health/ | grep -q "OK"; do sleep 5; done'

# Stop old container
docker ps | grep bmparliament_web | head -1 | awk '{print $1}' | xargs docker stop
```

## Monitoring During Deployment

```bash
# Terminal 1: Watch logs
docker logs -f bmparliament_web

# Terminal 2: Health checks
watch -n 1 'curl -s https://bmparliament.gov.ph/health/detailed/ | jq "{status: .status, errors: .errors}"'

# Terminal 3: Response times
while true; do time curl -s https://bmparliament.gov.ph/ > /dev/null; sleep 1; done
```

## Post-Deployment Verification

```bash
# 1. Verify migrations applied
docker exec bmparliament_web python manage.py showmigrations | grep -E "0023|0002"

# 2. Test ORM queries
docker exec bmparliament_web python manage.py shell << EOF
from apps.unified_db.models import PersonLink
link = PersonLink.objects.first()
print(f"✅ New field works: {link.bm_parliament_member}")
EOF

# 3. Monitor error rate (5 minutes)
for i in {1..30}; do
  errors=$(curl -s https://bmparliament.gov.ph/health/detailed/ | jq '.errors')
  echo "Check $i/30: Errors = $errors"
  [ "$errors" -gt 10 ] && echo "⚠️  High error rate!" || true
  sleep 10
done
```

## Emergency Rollback (< 5 minutes window)

```bash
# ONLY IF ERROR RATE > 50 in first 5 minutes

# 1. Stop new container
docker stop bmparliament_web

# 2. Rollback migrations
docker exec bmparliament_web python manage.py migrate unified_db 0001
docker exec bmparliament_web python manage.py migrate constituents 0022

# 3. Restart old code
git checkout HEAD~1
docker-compose up -d web

# 4. Clear caches
docker exec bmparliament_redis redis-cli -a $REDIS_PASSWORD FLUSHDB
```

## Key Metrics to Monitor

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Response Time | < 200ms | > 500ms | > 2000ms |
| Error Rate | 0% | > 5% | > 10% |
| DB Connections | 3-10 | > 20 | > 50 |

## Critical Thresholds

- **Error Rate > 10:** Investigate immediately
- **Error Rate > 50:** Initiate rollback (if within 5 minutes)
- **Response Time > 2s:** Check database locks
- **After 5 minutes:** Rollback unsafe, forward fix only

## Expected Behavior

✅ **Normal:**
- Migration completes in < 500ms
- Brief response time increase (250ms)
- Zero failed requests
- Health checks pass immediately after migration

❌ **Abnormal (requires investigation):**
- Migration takes > 5 seconds
- Error rate > 5%
- Health checks fail after 60 seconds
- Database connection errors

## Contacts

- **Technical Lead:** [Contact Info]
- **Database Admin:** [Contact Info]
- **DevOps Engineer:** [Contact Info]

## Resources

- **Full Analysis:** `/docs/deployment/ORM_FIELD_RENAME_PRODUCTION_DEPLOYMENT_ANALYSIS.md`
- **Sentry Dashboard:** https://sentry.io/organizations/bmparliament/issues/
- **Health Endpoint:** https://bmparliament.gov.ph/health/detailed/

---

**Document Version:** 1.0
**Last Updated:** November 19, 2025
**Status:** APPROVED FOR PRODUCTION
