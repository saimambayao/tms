#!/bin/bash

# #FahanieCares Platform - Media Files Backup Script
# Automated backup of uploaded media files with verification

set -euo pipefail

# Configuration from environment or defaults
MEDIA_DIR="${MEDIA_DIR:-/app/media}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/fahaniecares/media}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
EXCLUDE_PATTERNS="${EXCLUDE_PATTERNS:-*.tmp,*.log,cache/*,thumbnails/*}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$BACKUP_DIR/media_backup.log"
}

# Send notification function
send_notification() {
    local message="$1"
    local status="$2"
    
    log "$message"
    
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"📁 #FahanieCares Media Backup $status: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up media backups older than $RETENTION_DAYS days"
    find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
}

# Create media backup
create_media_backup() {
    log "Starting media files backup from $MEDIA_DIR"
    
    if [ ! -d "$MEDIA_DIR" ]; then
        log "WARNING: Media directory $MEDIA_DIR does not exist"
        return 0
    fi
    
    # Count files before backup
    local file_count=$(find "$MEDIA_DIR" -type f | wc -l)
    log "Found $file_count files in media directory"
    
    if [ "$file_count" -eq 0 ]; then
        log "No media files to backup"
        return 0
    fi
    
    # Create exclude list for tar
    local exclude_args=""
    IFS=',' read -ra EXCLUDES <<< "$EXCLUDE_PATTERNS"
    for pattern in "${EXCLUDES[@]}"; do
        exclude_args="$exclude_args --exclude=$pattern"
    done
    
    # Create compressed backup
    if tar czf "$BACKUP_FILE" $exclude_args -C "$(dirname "$MEDIA_DIR")" "$(basename "$MEDIA_DIR")" 2>>"$BACKUP_DIR/media_backup.log"; then
        log "Media backup created successfully: $BACKUP_FILE"
        
        # Verify the backup
        if verify_media_backup "$BACKUP_FILE"; then
            log "Media backup verification successful"
            return 0
        else
            log "ERROR: Media backup verification failed"
            return 1
        fi
    else
        log "ERROR: Media backup creation failed"
        return 1
    fi
}

# Verify media backup integrity
verify_media_backup() {
    local backup_file="$1"
    
    log "Verifying media backup integrity: $backup_file"
    
    # Check if file exists and is not empty
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        log "ERROR: Media backup file is missing or empty"
        return 1
    fi
    
    # Test tar.gz integrity
    if ! tar -tzf "$backup_file" >/dev/null 2>&1; then
        log "ERROR: Media backup file is corrupted (tar test failed)"
        return 1
    fi
    
    # Count files in backup
    local files_in_backup=$(tar -tzf "$backup_file" | grep -v '/$' | wc -l)
    log "Media backup contains $files_in_backup files"
    
    # Get backup file size
    local backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "unknown")
    log "Media backup verification passed - Size: $backup_size bytes"
    
    return 0
}

# Upload to S3 if configured
upload_media_to_s3() {
    local backup_file="$1"
    
    if [ -n "$S3_BUCKET" ] && command -v aws >/dev/null 2>&1; then
        log "Uploading media backup to S3: $S3_BUCKET"
        
        local s3_key="media-backups/$(basename "$backup_file")"
        
        if aws s3 cp "$backup_file" "s3://$S3_BUCKET/$s3_key"; then
            log "Media backup uploaded to S3 successfully: s3://$S3_BUCKET/$s3_key"
            
            # Set lifecycle for automatic cleanup
            aws s3api put-object-tagging \
                --bucket "$S3_BUCKET" \
                --key "$s3_key" \
                --tagging 'TagSet=[{Key=backup-type,Value=media},{Key=retention,Value=90days}]' 2>/dev/null || true
                
            return 0
        else
            log "ERROR: Failed to upload media backup to S3"
            return 1
        fi
    else
        log "S3 upload skipped (not configured or AWS CLI not available)"
        return 0
    fi
}

# Sync media to S3 (alternative to backup for large media collections)
sync_media_to_s3() {
    if [ -n "$S3_BUCKET" ] && command -v aws >/dev/null 2>&1; then
        log "Syncing media files directly to S3: $S3_BUCKET"
        
        local s3_path="s3://$S3_BUCKET/media-sync/"
        
        # Build exclude arguments for aws s3 sync
        local exclude_args=""
        IFS=',' read -ra EXCLUDES <<< "$EXCLUDE_PATTERNS"
        for pattern in "${EXCLUDES[@]}"; do
            exclude_args="$exclude_args --exclude \"$pattern\""
        done
        
        # Sync with versioning and metadata
        if eval aws s3 sync \"$MEDIA_DIR\" \"$s3_path\" $exclude_args --delete --storage-class STANDARD_IA; then
            log "Media sync to S3 completed successfully"
            return 0
        else
            log "ERROR: Media sync to S3 failed"
            return 1
        fi
    else
        log "S3 sync skipped (not configured or AWS CLI not available)"
        return 0
    fi
}

# Main media backup process
main() {
    log "=== Starting #FahanieCares Media Backup Process ==="
    
    # Clean up old backups first
    cleanup_old_backups
    
    # Determine backup strategy based on media size
    if [ -d "$MEDIA_DIR" ]; then
        local media_size=$(du -sb "$MEDIA_DIR" 2>/dev/null | cut -f1 || echo "0")
        local media_size_mb=$((media_size / 1024 / 1024))
        
        log "Media directory size: ${media_size_mb}MB"
        
        # For large media collections (>1GB), prefer S3 sync over backup
        if [ "$media_size_mb" -gt 1024 ] && [ -n "$S3_BUCKET" ]; then
            log "Large media collection detected, using S3 sync strategy"
            
            if sync_media_to_s3; then
                send_notification "Media files synced to S3 successfully (${media_size_mb}MB)" "SUCCESS"
                log "=== Media Sync Process Completed Successfully ==="
                exit 0
            else
                send_notification "Media sync to S3 failed" "FAILED"
                log "=== Media Sync Process Failed ==="
                exit 1
            fi
        fi
    fi
    
    # Standard backup process for smaller collections
    if create_media_backup; then
        # Upload to S3 if configured
        if upload_media_to_s3 "$BACKUP_FILE"; then
            send_notification "Media backup completed successfully" "SUCCESS"
            log "=== Media Backup Process Completed Successfully ==="
            exit 0
        else
            send_notification "Media backup created but S3 upload failed" "WARNING"
            log "=== Media Backup Process Completed with Warnings ==="
            exit 0
        fi
    else
        send_notification "Media backup process failed" "FAILED"
        log "=== Media Backup Process Failed ==="
        exit 1
    fi
}

# Handle script termination
trap 'log "Media backup script interrupted"; exit 1' INT TERM

# Run main function
main "$@"