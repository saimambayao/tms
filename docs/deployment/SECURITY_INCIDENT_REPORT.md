# Security Incident Report - Exposed Credentials in Git History

**Date**: 2025-11-20
**Status**: ⚠️ **IN PROGRESS - CREDENTIALS ROTATION REQUIRED**
**Severity**: HIGH - Production credentials exposed in git history

## Executive Summary

During a security audit of the BM Parliament repository, critical credentials were discovered in `.env` files tracked by Git. These files have been removed from current and historical git commits, but the credentials remain compromised and **must be rotated immediately**.

## Exposed Credentials

### 1. PostgreSQL Database Password ⚠️ **CRITICAL**
- **Service**: PostgreSQL Database
- **Exposed Value**: `glimpse2964`
- **Location**: `.env` file (DB_PASSWORD)
- **Status**: **MUST ROTATE IMMEDIATELY**
- **Impact**: Any user with git history access can connect to the production database

**Action Required**:
1. Change PostgreSQL password in Railway database settings
2. Update all connections (Django, backup scripts, monitoring)
3. Verify all services reconnect with new password

### 2. Gmail SMTP Password ⚠️ **CRITICAL**
- **Service**: Gmail Account (bmparliament@gmail.com)
- **Exposed Value**: `qelz rfne rucx nftz` (This is an app-specific password, not the main account password)
- **Location**: `.env` file (EMAIL_HOST_PASSWORD)
- **Status**: **MUST REVOKE IMMEDIATELY**
- **Impact**: Attackers can send emails on behalf of BM Parliament account

**Action Required**:
1. Go to Google Account Security Settings: https://myaccount.google.com/security
2. Navigate to "App passwords" for Gmail
3. Delete/revoke the compromised app password: `qelz rfne rucx nftz`
4. Create a new app password for Django email (Gmail requires app passwords for 3rd-party apps)
5. Update the `.env` file with the new app password

### 3. Database Dump File
- **Service**: Live PostgreSQL Database
- **File**: `src/db.sqlite3` (2.2 MB)
- **Exposed**: Entire production database with all data
- **Status**: **ASSUME COMPROMISED**
- **Impact**: All constituent data, user information, service records exposed

## Remediation Actions Completed ✅

### Git History Cleanup
- [x] Removed all `.env` files from git history (22 commits rewritten)
- [x] Removed `src/db.sqlite3` from git history
- [x] Force-pushed cleaned history to origin main
- [x] Updated `.gitignore` to prevent future commits of sensitive files
- [x] Rotated `DJANGO_SECRET_KEY` in production

### Future Prevention
- [x] `.gitignore` updated to prevent `.env`, `.env.*` files from being tracked
- [x] Database files (`db.sqlite3`) now ignored
- [x] Template files (`.env.example`, `.env.template`) kept in repo for configuration reference

## Remediation Actions Required NOW ⏱️

### 1. PostgreSQL Database Password Rotation
**Priority**: CRITICAL
**Timeline**: Within 24 hours

```bash
# On Railway Dashboard:
1. Go to your PostgreSQL service
2. Click "Connect"
3. Reset the password in the database credentials
4. Update Django settings with new password
5. Test connection from app
```

### 2. Gmail Account Security
**Priority**: CRITICAL
**Timeline**: Immediately (takes 2 minutes)

```
1. Go to https://myaccount.google.com/security
2. Scroll to "App passwords"
3. Select "Mail" and "macOS" (or appropriate device/app)
4. Revoke the old app password
5. Generate a new app password
6. Update .env with new password
7. Restart Django app
```

### 3. Database Backup & Security Audit
**Priority**: HIGH
**Timeline**: Within 48 hours

```
1. Create a fresh database dump/backup
2. Audit database access logs for any unauthorized access
3. If unauthorized access detected:
   - Flag potentially compromised records
   - Notify affected constituents
   - Report to appropriate authorities
4. Consider re-hashing passwords or resetting user accounts
```

### 4. Git Audit
**Priority**: MEDIUM
**Timeline**: Within 1 week

```
1. Check if any developers cloned the old version of the repo
2. Advise them to pull the cleaned history with: git pull --rebase
3. If they made local commits, help rebase onto new history
```

## Timeline of Events

1. **Initial Incident**: `.env` files with credentials were committed to git
2. **Detection**: Security audit discovered exposed files on 2025-11-20
3. **Immediate Actions Taken**:
   - Removed sensitive files from current git index
   - Updated `.gitignore` to prevent future commits
   - Cleaned entire git history using `git filter-branch`
   - Force-pushed cleaned history to origin
4. **Current Status**: Credentials remain exposed in git clone copies and mirrors
5. **Required Actions**: Rotate all exposed credentials

## Exposed Credentials Summary

| Credential | Service | Exposed Value | Status |
|------------|---------|---------------|--------|
| DB_PASSWORD | PostgreSQL | `glimpse2964` | ⚠️ NEEDS ROTATION |
| EMAIL_HOST_PASSWORD | Gmail | `qelz rfne rucx nftz` | ⚠️ NEEDS REVOCATION |
| Database Dump | Full DB | `src/db.sqlite3` | ⚠️ NEEDS AUDIT |
| DJANGO_SECRET_KEY | Django | *(rotated to Railway env var)* | ✅ ROTATED |

## Verification Steps

After completing rotation, verify with:

```bash
# Verify .env files are not in git history
git log --all --source --full-history -- .env | wc -l
# Should return: 0

# Verify database file is not in history
git log --all --source --full-history -- src/db.sqlite3 | wc -l
# Should return: 0

# Test database connection
python manage.py dbshell

# Test email sending
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'test', 'noreply@bmparliament.gov.ph', ['admin@example.com'])
```

## References

- [Git Filter-Repo Documentation](https://github.com/newren/git-filter-repo)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Google App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [PostgreSQL Password Security](https://www.postgresql.org/docs/current/sql-alterrole.html)

## Sign-Off

- [ ] Database password rotated
- [ ] Gmail app password revoked and new one created
- [ ] All connection strings updated in production
- [ ] Applications restarted and verified
- [ ] Database access audit completed
- [ ] Git history verified clean
- [ ] Team notified of security incident

---

**Report prepared**: 2025-11-20
**Last updated**: 2025-11-20
**Prepared by**: BM Parliament Development Team

