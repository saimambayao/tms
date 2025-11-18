#!/bin/bash

# #FahanieCares Platform - Backup Verification Script
# Automated verification of database and media backups

set -euo pipefail

# Configuration from environment or defaults
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares}"
S3_BUCKET="${S3_BUCKET:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
MAX_BACKUP_AGE_HOURS="${MAX_BACKUP_AGE_HOURS:-25}" # Alert if latest backup is older than 25 hours
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
TEST_DB_NAME="${TEST_DB_NAME:-fahaniecares_backup_test}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$BACKUP_DIR/verification.log"
}

# Send notification function
send_notification() {
    local message="$1"
    local status="$2"
    
    log "$message"
    
    if [ -n "$SLACK_WEBHOOK" ]; then
        local emoji="✅"
        case "$status" in
            "FAILED"|"ERROR") emoji="❌" ;;
            "WARNING") emoji="⚠️" ;;
            "INFO") emoji="ℹ️" ;;
        esac
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$emoji #FahanieCares Backup Verification: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# Verify database backups
verify_database_backups() {
    log "=== Verifying Database Backups ==="
    
    local db_backup_dir="$BACKUP_DIR"
    local latest_backup=""
    local backup_count=0
    local verification_errors=0
    
    # Find latest database backup
    for backup in "$db_backup_dir"/fahaniecares_backup_*.sql.gz; do
        if [ -f "$backup" ]; then
            ((backup_count++))
            if [ -z "$latest_backup" ] || [ "$backup" -nt "$latest_backup" ]; then
                latest_backup="$backup"
            fi
        fi
    done
    
    if [ "$backup_count" -eq 0 ]; then
        log "ERROR: No database backups found in $db_backup_dir"
        send_notification "No database backups found" "FAILED"
        return 1
    fi
    
    log "Found $backup_count database backup(s), latest: $(basename "$latest_backup")"
    
    # Check age of latest backup
    if [ -n "$latest_backup" ]; then
        local backup_age_hours=$(( ($(date +%s) - $(stat -f%m "$latest_backup" 2>/dev/null || stat -c%Y "$latest_backup" 2>/dev/null)) / 3600 ))
        log "Latest backup age: $backup_age_hours hours"
        
        if [ "$backup_age_hours" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
            log "WARNING: Latest backup is older than $MAX_BACKUP_AGE_HOURS hours"
            send_notification "Latest database backup is $backup_age_hours hours old (threshold: $MAX_BACKUP_AGE_HOURS)" "WARNING"
            ((verification_errors++))
        fi
    fi
    
    # Verify backup integrity
    for backup in "$db_backup_dir"/fahaniecares_backup_*.sql.gz; do
        if [ -f "$backup" ]; then
            log "Verifying backup: $(basename "$backup")"
            
            # Test gzip integrity
            if ! gzip -t "$backup" 2>/dev/null; then
                log "ERROR: Backup file is corrupted: $(basename "$backup")"
                ((verification_errors++))
                continue
            fi
            
            # Test SQL content
            if ! zcat "$backup" | head -20 | grep -q "PostgreSQL database dump"; then
                log "ERROR: Backup doesn't appear to be a valid PostgreSQL dump: $(basename "$backup")"
                ((verification_errors++))
                continue
            fi
            
            # Check backup size (should be at least 1KB for a real database)
            local backup_size=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup" 2>/dev/null || echo "0")
            if [ "$backup_size" -lt 1024 ]; then
                log "WARNING: Backup file seems too small: $(basename "$backup") ($backup_size bytes)"
                ((verification_errors++))
                continue
            fi
            
            log "✓ Backup verification passed: $(basename "$backup") ($backup_size bytes)"
        fi
    done
    
    return $verification_errors
}

# Test database backup restore (optional - only if test database is configured)
test_database_restore() {
    if [ -z "${DB_PASSWORD:-}" ]; then
        log "Skipping database restore test (DB_PASSWORD not set)"
        return 0
    fi
    
    local latest_backup=""
    for backup in "$BACKUP_DIR"/fahaniecares_backup_*.sql.gz; do
        if [ -f "$backup" ]; then
            if [ -z "$latest_backup" ] || [ "$backup" -nt "$latest_backup" ]; then
                latest_backup="$backup"
            fi
        fi
    done
    
    if [ -z "$latest_backup" ]; then
        log "No database backup found for restore test"
        return 1
    fi
    
    log "Testing database restore from: $(basename "$latest_backup")"
    
    # Drop test database if it exists
    PGPASSWORD="$DB_PASSWORD" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --if-exists "$TEST_DB_NAME" 2>/dev/null || true
    
    # Create test database
    if ! PGPASSWORD="$DB_PASSWORD" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$TEST_DB_NAME" 2>/dev/null; then
        log "ERROR: Failed to create test database"
        return 1
    fi
    
    # Restore backup to test database
    if zcat "$latest_backup" | PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" >/dev/null 2>&1; then
        log "✓ Database restore test passed"
        
        # Test basic query
        local table_count=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs || echo "0")
        log "Restored database contains $table_count tables"
        
        # Cleanup test database
        PGPASSWORD="$DB_PASSWORD" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$TEST_DB_NAME" 2>/dev/null || true
        
        return 0
    else
        log "ERROR: Database restore test failed"
        PGPASSWORD="$DB_PASSWORD" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --if-exists "$TEST_DB_NAME" 2>/dev/null || true
        return 1
    fi
}

# Verify media backups
verify_media_backups() {
    log "=== Verifying Media Backups ==="
    
    local media_backup_dir="$BACKUP_DIR/media"
    local backup_count=0
    local verification_errors=0
    
    # Create media backup directory if it doesn't exist
    mkdir -p "$media_backup_dir"
    
    # Find media backups
    for backup in "$media_backup_dir"/media_backup_*.tar.gz; do
        if [ -f "$backup" ]; then
            ((backup_count++))
            log "Verifying media backup: $(basename "$backup")"
            
            # Test tar.gz integrity
            if ! tar -tzf "$backup" >/dev/null 2>&1; then
                log "ERROR: Media backup file is corrupted: $(basename "$backup")"
                ((verification_errors++))
                continue
            fi
            
            # Check backup size
            local backup_size=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup" 2>/dev/null || echo "0")
            local file_count=$(tar -tzf "$backup" | grep -v '/$' | wc -l)
            
            log "✓ Media backup verification passed: $(basename "$backup") ($backup_size bytes, $file_count files)"
        fi
    done
    
    if [ "$backup_count" -eq 0 ]; then
        log "INFO: No media backups found (may be using S3 sync instead)"
        return 0
    fi
    
    log "Verified $backup_count media backup(s)"
    return $verification_errors
}

# Verify S3 backups if configured
verify_s3_backups() {
    if [ -z "$S3_BUCKET" ] || ! command -v aws >/dev/null 2>&1; then
        log "Skipping S3 backup verification (not configured or AWS CLI not available)"
        return 0
    fi
    
    log "=== Verifying S3 Backups ==="
    
    local verification_errors=0
    
    # Check database backups in S3
    local db_backup_count=$(aws s3 ls "s3://$S3_BUCKET/database-backups/" 2>/dev/null | wc -l || echo "0")
    if [ "$db_backup_count" -gt 0 ]; then
        log "Found $db_backup_count database backup(s) in S3"
        
        # Get latest database backup info
        local latest_s3_backup=$(aws s3 ls "s3://$S3_BUCKET/database-backups/" --recursive | sort | tail -1 | awk '{print $4}' || echo "")
        if [ -n "$latest_s3_backup" ]; then
            log "Latest S3 database backup: $latest_s3_backup"
        fi
    else
        log "WARNING: No database backups found in S3"
        ((verification_errors++))
    fi
    
    # Check media backups/sync in S3
    local media_backup_count=$(aws s3 ls "s3://$S3_BUCKET/media-backups/" 2>/dev/null | wc -l || echo "0")
    local media_sync_count=$(aws s3 ls "s3://$S3_BUCKET/media-sync/" 2>/dev/null | wc -l || echo "0")
    
    if [ "$media_backup_count" -gt 0 ]; then
        log "Found $media_backup_count media backup(s) in S3"
    elif [ "$media_sync_count" -gt 0 ]; then
        log "Found $media_sync_count synced media file(s) in S3"
    else
        log "INFO: No media backups or sync found in S3 (may not be needed if no media files exist)"
    fi
    
    return $verification_errors
}

# Generate backup status report
generate_report() {
    local total_errors="$1"
    
    log "=== Backup Verification Report ==="
    
    # Database backup summary
    local db_backup_count=$(find "$BACKUP_DIR" -name "fahaniecares_backup_*.sql.gz" -type f | wc -l)
    log "Local database backups: $db_backup_count"
    
    # Media backup summary
    local media_backup_count=$(find "$BACKUP_DIR/media" -name "media_backup_*.tar.gz" -type f 2>/dev/null | wc -l || echo "0")
    log "Local media backups: $media_backup_count"
    
    # S3 summary
    if [ -n "$S3_BUCKET" ] && command -v aws >/dev/null 2>&1; then
        local s3_db_count=$(aws s3 ls "s3://$S3_BUCKET/database-backups/" 2>/dev/null | wc -l || echo "0")
        local s3_media_count=$(aws s3 ls "s3://$S3_BUCKET/media-backups/" --recursive 2>/dev/null | wc -l || echo "0")
        log "S3 database backups: $s3_db_count"
        log "S3 media backups: $s3_media_count"
    fi
    
    log "Total verification errors: $total_errors"
    
    if [ "$total_errors" -eq 0 ]; then
        log "✓ All backup verifications passed"
        return 0
    else
        log "✗ $total_errors verification errors found"
        return 1
    fi
}

# Main verification process
main() {
    log "=== Starting #FahanieCares Backup Verification ==="
    
    local total_errors=0
    
    # Verify database backups
    if ! verify_database_backups; then
        ((total_errors += $?))
    fi
    
    # Test database restore if configured
    if [ "${TEST_RESTORE:-false}" = "true" ]; then
        if ! test_database_restore; then
            ((total_errors++))
        fi
    fi
    
    # Verify media backups
    if ! verify_media_backups; then
        ((total_errors += $?))
    fi
    
    # Verify S3 backups
    if ! verify_s3_backups; then
        ((total_errors += $?))
    fi
    
    # Generate final report
    if generate_report "$total_errors"; then
        send_notification "Backup verification completed successfully" "SUCCESS"
        log "=== Backup Verification Completed Successfully ==="
        exit 0
    else
        send_notification "Backup verification completed with $total_errors error(s)" "FAILED"
        log "=== Backup Verification Completed with Errors ==="
        exit 1
    fi
}

# Handle script termination
trap 'log "Backup verification script interrupted"; exit 1' INT TERM

# Run main function
main "$@"