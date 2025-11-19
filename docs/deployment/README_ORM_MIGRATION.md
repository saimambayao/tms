# ORM Field Rename Migration - Documentation Index

This directory contains comprehensive documentation for the production deployment of the ORM field rename migration (fahanie_cares_member → bm_parliament_member).

---

## Quick Start

**For Deployment Engineers:**
1. Read: [Executive Summary](#executive-summary) (5 minutes)
2. Review: [Quick Reference Guide](#quick-reference-guide) (2 minutes)
3. Execute: [Automated Deployment Script](#deployment-script)
4. Monitor: [Post-Deployment Checklist](#post-deployment)

**For Stakeholders:**
- Read: [Executive Summary](#executive-summary)
- Risk Level: **LOW** ✅
- Expected Downtime: **0 seconds**
- Deployment Duration: **~12 minutes**

---

## Documentation Structure

### 1. Executive Summary
**File:** `EXECUTIVE_SUMMARY_ORM_MIGRATION.md`
**Audience:** Technical leads, stakeholders, decision-makers
**Length:** 5 pages
**Purpose:** High-level overview of risks, strategy, and recommendations

**Key Sections:**
- Migration scope and affected components
- Risk assessment matrix
- Deployment strategy recommendation
- Success criteria and approval status

**When to Read:** Before making deployment decision

### 2. Full Risk Analysis
**File:** `ORM_FIELD_RENAME_PRODUCTION_DEPLOYMENT_ANALYSIS.md`
**Audience:** DevOps engineers, database administrators
**Length:** 50+ pages
**Purpose:** Deep technical analysis of all deployment scenarios

**Key Sections:**
1. Zero-Downtime Deployment Feasibility
2. Code Deployment Ordering
3. Rollback Complexity
4. Concurrent Request Handling
5. Cache Invalidation
6. Database Replication Issues
7. Monitoring and Observability
8. Emergency Abort/Quick Stop
9. Testing Recommendations
10. Safe Deployment Procedure
11. Rollback Plan and Procedure
12. Emergency Procedures

**When to Read:** Before deployment execution, reference during deployment

### 3. Quick Reference Guide
**File:** `DEPLOYMENT_QUICK_REFERENCE.md`
**Audience:** Deployment engineers (hands-on)
**Length:** 2 pages
**Purpose:** Command-line reference for deployment day

**Key Sections:**
- Pre-deployment checklist (copy-paste commands)
- Deployment command (single command)
- Monitoring commands (real-time)
- Post-deployment verification
- Emergency rollback (< 5 minutes)

**When to Read:** During deployment execution (keep open in terminal)

### 4. Automated Deployment Script
**File:** `/deployment/scripts/deploy_field_rename_migration.sh`
**Audience:** DevOps engineers
**Length:** 600+ lines
**Purpose:** Fully automated deployment with safety checks

**Features:**
- ✅ Pre-deployment health checks
- ✅ Automatic database backup
- ✅ Blue-Green deployment
- ✅ Migration verification
- ✅ 5-minute error monitoring with auto-rollback
- ✅ Cleanup and reporting

**Usage:**
```bash
# Standard deployment
./deploy_field_rename_migration.sh

# Dry run (no changes)
./deploy_field_rename_migration.sh --dry-run

# Emergency rollback
./deploy_field_rename_migration.sh --force-rollback
```

---

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT TIMELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  T-24h: Staging Validation Complete                        │
│         └─> Review Full Risk Analysis                       │
│                                                              │
│  T-1h:  Deployment Team Assembled                           │
│         ├─> Pre-deployment checklist                        │
│         ├─> Open monitoring dashboards                      │
│         └─> Verify production health                        │
│                                                              │
│  T-0:   Execute Deployment Script                           │
│         ├─> Database backup (2 min)                        │
│         ├─> Build new container (3 min)                    │
│         ├─> Deploy Blue-Green (2 min)                      │
│         └─> Health checks pass (1 min)                     │
│                                                              │
│  T+5m:  Verification Complete                               │
│         ├─> Migration status verified                       │
│         ├─> ORM queries tested                              │
│         ├─> Error rate monitored (5 min)                   │
│         └─> Old container stopped                           │
│                                                              │
│  T+15m: Deployment Complete                                 │
│         ├─> Auto-rollback window closed                     │
│         ├─> Deployment report generated                     │
│         └─> Team dismissed (on-call monitoring)             │
│                                                              │
│  T+1h:  Short-term Monitoring                               │
│         └─> Review logs for anomalies                       │
│                                                              │
│  T+24h: Long-term Validation                                │
│         ├─> Sentry error review                            │
│         ├─> Performance metrics analysis                    │
│         └─> Lessons learned documentation                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Decision Points

### Should We Deploy?

**YES, if:**
- ✅ Staging environment tests passed
- ✅ Production health status is "healthy"
- ✅ Error rate < 5% in last 24 hours
- ✅ Deployment team available for 1 hour
- ✅ Database backup completed successfully

**NO, if:**
- ❌ Production currently experiencing issues
- ❌ High traffic period (avoid daytime deployment)
- ❌ Recent deployment within last 48 hours
- ❌ Critical features broken in staging

### Which Deployment Strategy?

**Blue-Green (RECOMMENDED):**
- ✅ Zero user-visible downtime
- ✅ Automatic rollback on health check failure
- ✅ No connection pool saturation
- ❌ Requires Coolify/Docker setup (already configured)

**Single Container (ACCEPTABLE):**
- ✅ Simpler execution
- ⚠️ Brief downtime (~5 seconds)
- ❌ No automatic rollback mechanism

**Maintenance Window (CONSERVATIVE):**
- ✅ Fully controlled environment
- ❌ 5-minute user-visible downtime
- ❌ Unnecessary for this migration

**Verdict:** Use **Blue-Green** via automated script

### When to Rollback?

**Auto-Rollback Triggers (0-5 minutes):**
- Error rate > 10
- Health checks fail after 60 seconds
- Migration verification fails
- ORM query tests fail

**Manual Rollback (5-30 minutes):**
- Unusual error patterns detected
- Performance degradation > 50%
- Team consensus for rollback

**Forward Fix Only (30+ minutes):**
- Too much production data written to new schema
- Rollback would cause data loss
- Deploy bug fix instead

---

## Monitoring Checklist

### Pre-Deployment Baseline

```bash
# Capture baseline metrics
curl -s https://bmparliament.gov.ph/health/detailed/ | jq '.' > baseline_metrics.json

# Expected values:
# - status: "healthy"
# - errors: 0-5
# - response_time_ms: < 200
# - database.connections: 3-10
```

### During Deployment

**Watch These Terminals:**
```bash
# Terminal 1: Deployment script output
./deploy_field_rename_migration.sh

# Terminal 2: Health endpoint
watch -n 1 'curl -s https://bmparliament.gov.ph/health/detailed/ | jq "{status: .status, errors: .errors}"'

# Terminal 3: Response times
while true; do time curl -s https://bmparliament.gov.ph/ > /dev/null; sleep 1; done

# Terminal 4: Sentry dashboard
open https://sentry.io/organizations/bmparliament/issues/
```

### Post-Deployment Verification

```bash
# 1. Verify migrations applied
docker exec bmparliament_web python manage.py showmigrations | grep -E "0023|0002"
# Expected: [X] 0023... and [X] 0002...

# 2. Test ORM queries
docker exec bmparliament_web python manage.py shell << EOF
from apps.unified_db.models import PersonLink
link = PersonLink.objects.first()
print(f"✅ Works: {link.bm_parliament_member}")
EOF

# 3. Check error rate
curl -s https://bmparliament.gov.ph/health/detailed/ | jq '.errors'
# Expected: 0-5

# 4. Review Sentry
# Visit: https://sentry.io/organizations/bmparliament/issues/?query=is:unresolved
# Expected: No new errors
```

---

## Emergency Procedures

### High Error Rate Detected (> 10 errors)

```bash
# 1. Check if within rollback window (< 5 minutes)
echo "Deployment started: [TIME]"
echo "Current time: $(date)"
echo "Elapsed: [X] minutes"

# 2. If within 5 minutes: AUTO-ROLLBACK
./deploy_field_rename_migration.sh --force-rollback

# 3. If beyond 5 minutes: INVESTIGATE FIRST
# - Check Sentry for error patterns
# - Verify database schema is correct
# - Check if errors are related to migration
# - Consider forward fix instead of rollback
```

### Migration Failed to Apply

```bash
# Symptom: Health checks fail, container won't start

# 1. Check migration logs
docker logs bmparliament_web | grep -A 10 "migrate"

# 2. Verify database state
docker exec bmparliament_db psql -U bmparliament_user -d bmparliament_prod -c "
SELECT * FROM django_migrations WHERE app = 'unified_db' ORDER BY id DESC LIMIT 5;
"

# 3. If migration stuck: ROLLBACK IMMEDIATELY
./deploy_field_rename_migration.sh --force-rollback

# 4. Investigate root cause before retry
```

### Container Won't Start After Migration

```bash
# 1. Keep old container running (don't panic!)
docker ps | grep bmparliament_web
# Old container should still be serving traffic

# 2. Check new container logs
docker logs bmparliament_web_new

# 3. Let Coolify/Docker handle it
# - Health checks will fail
# - Traffic won't switch to broken container
# - Old container continues serving

# 4. Fix and redeploy
# Or rollback if within 5-minute window
```

---

## Common Questions

**Q: What if I need to rollback after 5 minutes?**
A: Rollback is still possible but requires data preservation. See full analysis Section 12 for procedure. Generally, forward fix is safer.

**Q: Can I deploy during business hours?**
A: Not recommended. Deploy during low-traffic period (2:00 AM Manila time) to minimize risk.

**Q: What if the automated script fails?**
A: Script includes comprehensive error handling. If it fails, it will print clear error message and safe state to rollback from.

**Q: How do I know if deployment was successful?**
A: Script will display "🎉 DEPLOYMENT SUCCESSFUL" banner and generate report in `/logs/deployment_report_*.md`

**Q: What's the worst-case scenario?**
A: Migration fails, auto-rollback triggers, platform restored to previous state within 2 minutes. Zero data loss.

**Q: Do I need to notify users?**
A: No. Zero downtime deployment means users won't notice. Optional: Post-deployment announcement about backend improvements.

---

## Support Contacts

**During Deployment:**
- Technical Lead: [Contact Info]
- Database Administrator: [Contact Info]
- DevOps Engineer: [Contact Info]

**Post-Deployment Issues:**
- Sentry Dashboard: https://sentry.io/organizations/bmparliament/issues/
- Health Endpoint: https://bmparliament.gov.ph/health/detailed/
- Emergency Hotline: [Contact Info]

**Documentation Issues:**
- Report to: dev@bmparliament.gov.ph
- GitHub Issues: [Repository URL]

---

## File Locations

```
docs/deployment/
├── README_ORM_MIGRATION.md                    (This file)
├── EXECUTIVE_SUMMARY_ORM_MIGRATION.md         (5 pages - decision makers)
├── ORM_FIELD_RENAME_PRODUCTION_DEPLOYMENT_ANALYSIS.md  (50+ pages - technical deep dive)
└── DEPLOYMENT_QUICK_REFERENCE.md              (2 pages - command cheatsheet)

deployment/scripts/
└── deploy_field_rename_migration.sh           (Automated deployment script)

backups/
├── pre_migration_[timestamp].sql.gz           (Created during deployment)
└── rollback_data_backup.csv                   (Created if rollback needed)

logs/
├── deployment_[timestamp].log                 (Full deployment log)
└── deployment_report_[timestamp].md           (Post-deployment report)
```

---

## Version History

**v1.0 - November 19, 2025**
- Initial comprehensive analysis
- Blue-Green deployment strategy
- Automated deployment script
- Emergency procedures documented

---

## Next Steps

1. **Review Documents:**
   - [ ] Executive Summary (required for all team members)
   - [ ] Full Risk Analysis (required for deployment engineers)
   - [ ] Quick Reference (bookmark for deployment day)

2. **Test Staging:**
   - [ ] Validate migration on staging environment
   - [ ] Load test during migration execution
   - [ ] Practice rollback procedure

3. **Schedule Deployment:**
   - [ ] Select low-traffic window (2:00 AM recommended)
   - [ ] Notify stakeholders
   - [ ] Assemble deployment team

4. **Execute Deployment:**
   - [ ] Run automated script
   - [ ] Monitor for 5 minutes
   - [ ] Verify success
   - [ ] Generate report

5. **Post-Deployment:**
   - [ ] 24-hour error monitoring
   - [ ] Performance metrics review
   - [ ] Document lessons learned

---

**Documentation Prepared By:** Claude Code (Anthropic)
**Last Updated:** November 19, 2025
**Status:** ✅ Complete and ready for production deployment
