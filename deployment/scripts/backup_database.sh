#!/bin/bash

# #FahanieCares Platform - Database Backup Script
# Automated PostgreSQL database backup with verification

set -euo pipefail

# Configuration from environment or defaults
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-fahaniecares_db}"
DB_USER="${DB_USER:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
S3_BUCKET="${S3_BUCKET:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/fahaniecares_backup_$TIMESTAMP.sql"
BACKUP_COMPRESSED="$BACKUP_FILE.gz"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$BACKUP_DIR/backup.log"
}

# Send notification function
send_notification() {
    local message="$1"
    local status="$2"
    
    log "$message"
    
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🗄️ #FahanieCares Backup $status: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days"
    find "$BACKUP_DIR" -name "fahaniecares_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "fahaniecares_backup_*.sql" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
}

# Create database backup
create_backup() {
    log "Starting database backup for $DB_NAME"
    
    # Create backup with pg_dump
    if PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --clean \
        --if-exists \
        --create \
        > "$BACKUP_FILE" 2>>"$BACKUP_DIR/backup.log"; then
        
        log "Database backup created successfully: $BACKUP_FILE"
        
        # Compress the backup
        if gzip "$BACKUP_FILE"; then
            log "Backup compressed successfully: $BACKUP_COMPRESSED"
            
            # Verify the compressed backup
            if verify_backup "$BACKUP_COMPRESSED"; then
                log "Backup verification successful"
                return 0
            else
                log "ERROR: Backup verification failed"
                return 1
            fi
        else
            log "ERROR: Failed to compress backup"
            return 1
        fi
    else
        log "ERROR: Database backup failed"
        return 1
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    log "Verifying backup integrity: $backup_file"
    
    # Check if file exists and is not empty
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        log "ERROR: Backup file is missing or empty"
        return 1
    fi
    
    # Test gzip integrity
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log "ERROR: Backup file is corrupted (gzip test failed)"
        return 1
    fi
    
    # Test SQL validity by checking for essential patterns
    if ! zcat "$backup_file" | head -20 | grep -q "PostgreSQL database dump"; then
        log "ERROR: Backup file doesn't appear to be a valid PostgreSQL dump"
        return 1
    fi
    
    # Get backup file size
    local backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "unknown")
    log "Backup verification passed - Size: $backup_size bytes"
    
    return 0
}

# Upload to S3 if configured
upload_to_s3() {
    local backup_file="$1"
    
    if [ -n "$S3_BUCKET" ] && command -v aws >/dev/null 2>&1; then
        log "Uploading backup to S3: $S3_BUCKET"
        
        local s3_key="database-backups/$(basename "$backup_file")"
        
        if aws s3 cp "$backup_file" "s3://$S3_BUCKET/$s3_key"; then
            log "Backup uploaded to S3 successfully: s3://$S3_BUCKET/$s3_key"
            
            # Set lifecycle for automatic cleanup
            aws s3api put-object-tagging \
                --bucket "$S3_BUCKET" \
                --key "$s3_key" \
                --tagging 'TagSet=[{Key=backup-type,Value=database},{Key=retention,Value=30days}]' 2>/dev/null || true
                
            return 0
        else
            log "ERROR: Failed to upload backup to S3"
            return 1
        fi
    else
        log "S3 upload skipped (not configured or AWS CLI not available)"
        return 0
    fi
}

# Main backup process
main() {
    log "=== Starting #FahanieCares Database Backup Process ==="
    
    # Check required environment variables
    if [ -z "${DB_PASSWORD:-}" ]; then
        log "ERROR: DB_PASSWORD environment variable is required"
        send_notification "Database backup failed - DB_PASSWORD not set" "FAILED"
        exit 1
    fi
    
    # Check if pg_dump is available
    if ! command -v pg_dump >/dev/null 2>&1; then
        log "ERROR: pg_dump command not found"
        send_notification "Database backup failed - pg_dump not available" "FAILED"
        exit 1
    fi
    
    # Clean up old backups first
    cleanup_old_backups
    
    # Create and verify backup
    if create_backup; then
        # Upload to S3 if configured
        if upload_to_s3 "$BACKUP_COMPRESSED"; then
            send_notification "Database backup completed successfully" "SUCCESS"
            log "=== Database Backup Process Completed Successfully ==="
            exit 0
        else
            send_notification "Database backup created but S3 upload failed" "WARNING"
            log "=== Database Backup Process Completed with Warnings ==="
            exit 0
        fi
    else
        send_notification "Database backup process failed" "FAILED"
        log "=== Database Backup Process Failed ==="
        exit 1
    fi
}

# Handle script termination
trap 'log "Backup script interrupted"; exit 1' INT TERM

# Run main function
main "$@"