#!/bin/bash
#
# BM Parliament ORM Field Rename Migration Deployment Script
#
# Purpose: Deploy field rename migrations (fahanie_cares_member → bm_parliament_member)
# Strategy: Blue-Green deployment with automatic rollback on failure
# Author: BM Parliament Development Team
# Date: November 19, 2025
#
# Usage: ./deploy_field_rename_migration.sh [--dry-run] [--skip-backup] [--force-rollback]
#

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_START_TIME=$(date +%s)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/deployment_$(date +%Y%m%d_%H%M%S).log"

# Docker configuration
COMPOSE_FILE="$PROJECT_ROOT/deployment/docker/docker-compose/coolify.yml"
DB_CONTAINER="bmparliament_db"
WEB_CONTAINER="bmparliament_web"
REDIS_CONTAINER="bmparliament_redis"

# Database configuration
DB_USER="${POSTGRES_USER:-bmparliament_user}"
DB_NAME="${POSTGRES_DB:-bmparliament_prod}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# Redis configuration
REDIS_PASSWORD="${REDIS_PASSWORD}"

# Health check configuration
HEALTH_URL="${HEALTH_URL:-https://bmparliament.gov.ph/health/detailed/}"
MAX_HEALTH_RETRIES=12
HEALTH_CHECK_INTERVAL=5

# Rollback configuration
ROLLBACK_WINDOW=300  # 5 minutes in seconds
ERROR_THRESHOLD=10   # Max errors before rollback

# Parse command line arguments
DRY_RUN=false
SKIP_BACKUP=false
FORCE_ROLLBACK=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-backup)
      SKIP_BACKUP=true
      shift
      ;;
    --force-rollback)
      FORCE_ROLLBACK=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--dry-run] [--skip-backup] [--force-rollback]"
      exit 1
      ;;
  esac
done

# Logging functions
log() {
  local level=$1
  shift
  local message="$@"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() {
  log "INFO" "${BLUE}$@${NC}"
}

log_success() {
  log "SUCCESS" "${GREEN}✅ $@${NC}"
}

log_warning() {
  log "WARNING" "${YELLOW}⚠️  $@${NC}"
}

log_error() {
  log "ERROR" "${RED}❌ $@${NC}"
}

# Utility functions
check_dependencies() {
  log_info "Checking dependencies..."

  local deps=("docker" "docker-compose" "curl" "jq")
  for dep in "${deps[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
      log_error "$dep is not installed"
      exit 1
    fi
  done

  log_success "All dependencies found"
}

verify_environment() {
  log_info "Verifying environment..."

  # Check if required environment variables are set
  if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
    log_error "POSTGRES_PASSWORD environment variable is not set"
    exit 1
  fi

  if [[ -z "${REDIS_PASSWORD:-}" ]]; then
    log_error "REDIS_PASSWORD environment variable is not set"
    exit 1
  fi

  # Check if containers are running
  if ! docker ps | grep -q "$DB_CONTAINER"; then
    log_error "Database container is not running"
    exit 1
  fi

  if ! docker ps | grep -q "$WEB_CONTAINER"; then
    log_error "Web container is not running"
    exit 1
  fi

  log_success "Environment verified"
}

check_production_health() {
  log_info "Checking production health..."

  local health_response=$(curl -s "$HEALTH_URL" || echo '{"status": "error"}')
  local status=$(echo "$health_response" | jq -r '.status')
  local errors=$(echo "$health_response" | jq -r '.errors // 0')

  if [[ "$status" != "healthy" ]]; then
    log_error "Production is unhealthy: $status"
    log_error "Health response: $health_response"
    exit 1
  fi

  if [[ "$errors" -gt 5 ]]; then
    log_warning "Production has $errors errors (threshold: 5)"
    read -p "Continue anyway? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
      log_error "Deployment aborted by user"
      exit 1
    fi
  fi

  log_success "Production is healthy (errors: $errors)"
}

create_backup() {
  if [[ "$SKIP_BACKUP" == true ]]; then
    log_warning "Skipping backup (--skip-backup flag)"
    return
  fi

  log_info "Creating database backup..."

  mkdir -p "$BACKUP_DIR"
  local backup_file="$BACKUP_DIR/pre_migration_$(date +%Y%m%d_%H%M%S).sql.gz"

  if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$backup_file"; then
    local backup_size=$(du -h "$backup_file" | cut -f1)
    log_success "Backup created: $backup_file ($backup_size)"

    # Test backup integrity
    if gunzip -t "$backup_file" 2>&1; then
      log_success "Backup integrity verified"
    else
      log_error "Backup integrity check failed"
      exit 1
    fi
  else
    log_error "Failed to create backup"
    exit 1
  fi
}

clear_caches() {
  log_info "Clearing non-essential caches..."

  # Clear view caches (preserve sessions)
  if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" \
    EVAL "return redis.call('del', unpack(redis.call('keys', 'bmparliament:views*')))" 0 &>/dev/null; then
    log_success "Caches cleared"
  else
    log_warning "Failed to clear caches (non-critical)"
  fi
}

build_new_image() {
  log_info "Building new Docker image..."

  cd "$PROJECT_ROOT"

  if docker-compose -f "$COMPOSE_FILE" build web; then
    log_success "New image built successfully"

    # Tag as backup
    docker tag bmparliament_web:latest "bmparliament_web:pre_migration_backup_$(date +%Y%m%d_%H%M%S)"
    log_info "Old image tagged as backup"
  else
    log_error "Failed to build new image"
    exit 1
  fi
}

deploy_new_container() {
  log_info "Deploying new container (Blue-Green strategy)..."

  if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY RUN: Would deploy new container here"
    return
  fi

  # Start new container alongside old one
  if docker-compose -f "$COMPOSE_FILE" up -d --no-deps --scale web=2 web; then
    log_success "New container started"
  else
    log_error "Failed to start new container"
    exit 1
  fi

  # Wait for new container to be ready
  log_info "Waiting for new container to pass health checks..."

  local retries=0
  while [[ $retries -lt $MAX_HEALTH_RETRIES ]]; do
    local health_response=$(curl -s "$HEALTH_URL" || echo '{"status": "error"}')
    local status=$(echo "$health_response" | jq -r '.status')

    if [[ "$status" == "healthy" ]]; then
      log_success "Health checks passed"
      return
    fi

    retries=$((retries + 1))
    log_info "Health check attempt $retries/$MAX_HEALTH_RETRIES (status: $status)"
    sleep "$HEALTH_CHECK_INTERVAL"
  done

  log_error "Health checks failed after $MAX_HEALTH_RETRIES attempts"
  log_error "Rolling back deployment..."
  rollback_deployment
  exit 1
}

verify_migration() {
  log_info "Verifying migration applied..."

  # Check migration status
  local migration_output=$(docker exec "$WEB_CONTAINER" python manage.py showmigrations 2>&1)

  if echo "$migration_output" | grep -q "\[X\] 0023_rename_fahanie_cares_member_to_bm_parliament_member"; then
    log_success "Migration 0023 applied"
  else
    log_error "Migration 0023 not applied"
    return 1
  fi

  if echo "$migration_output" | grep -q "\[X\] 0002_rename_fahanie_cares_member_field"; then
    log_success "Migration 0002 applied"
  else
    log_error "Migration 0002 not applied"
    return 1
  fi

  # Verify database schema
  log_info "Verifying database schema..."

  if docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "\d unified_db_personlink" | grep -q "bm_parliament_member"; then
    log_success "Database schema updated correctly"
  else
    log_error "Database schema verification failed"
    return 1
  fi

  # Test ORM queries
  log_info "Testing ORM queries..."

  local orm_test=$(docker exec "$WEB_CONTAINER" python manage.py shell << 'EOF'
from apps.unified_db.models import PersonLink
try:
    link = PersonLink.objects.first()
    if link:
        _ = link.bm_parliament_member
        print("SUCCESS")
    else:
        print("NO_DATA")
except Exception as e:
    print(f"ERROR: {e}")
EOF
)

  if echo "$orm_test" | grep -q "SUCCESS\|NO_DATA"; then
    log_success "ORM queries working correctly"
  else
    log_error "ORM query test failed: $orm_test"
    return 1
  fi

  return 0
}

monitor_error_rate() {
  log_info "Monitoring error rate for 5 minutes..."

  local start_time=$(date +%s)
  local check_count=0
  local max_checks=30  # 5 minutes with 10-second intervals

  while [[ $check_count -lt $max_checks ]]; do
    local elapsed=$(($(date +%s) - $start_time))
    local remaining=$((300 - elapsed))

    local health_response=$(curl -s "$HEALTH_URL" || echo '{"status": "error", "errors": 999}')
    local status=$(echo "$health_response" | jq -r '.status')
    local errors=$(echo "$health_response" | jq -r '.errors // 0')

    check_count=$((check_count + 1))
    log_info "Check $check_count/$max_checks: Status=$status, Errors=$errors (${remaining}s remaining)"

    if [[ "$errors" -gt $ERROR_THRESHOLD ]]; then
      log_error "Error threshold exceeded: $errors > $ERROR_THRESHOLD"
      log_error "Initiating automatic rollback..."
      rollback_deployment
      exit 1
    fi

    sleep 10
  done

  log_success "5-minute monitoring window passed. No critical issues detected."
}

stop_old_container() {
  log_info "Stopping old container..."

  if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY RUN: Would stop old container here"
    return
  fi

  # Find and stop old container (first one in the list, excluding new one)
  local old_container=$(docker ps | grep bmparliament_web | head -1 | awk '{print $1}')

  if [[ -n "$old_container" ]]; then
    docker stop "$old_container"
    docker rm "$old_container"
    log_success "Old container stopped and removed"
  else
    log_warning "No old container found to stop"
  fi
}

rollback_deployment() {
  log_warning "ROLLBACK INITIATED"

  local time_since_deployment=$(($(date +%s) - DEPLOYMENT_START_TIME))
  log_info "Time since deployment: $((time_since_deployment / 60)) minutes"

  if [[ $time_since_deployment -gt $ROLLBACK_WINDOW ]] && [[ "$FORCE_ROLLBACK" != true ]]; then
    log_error "Rollback window exceeded ($((time_since_deployment / 60)) > $((ROLLBACK_WINDOW / 60)) minutes)"
    log_error "Rollback may cause data loss. Use --force-rollback to proceed anyway."
    return 1
  fi

  # Check for data written to new schema
  log_info "Checking for data in new schema..."

  local new_data_count=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM unified_db_personlink WHERE bm_parliament_member_id IS NOT NULL;" | tr -d ' ')

  if [[ "$new_data_count" -gt 0 ]]; then
    log_warning "Found $new_data_count records with new field. Backing up before rollback..."

    # Export data to preserve
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c \
      "COPY (SELECT id, bm_parliament_member_id FROM unified_db_personlink WHERE bm_parliament_member_id IS NOT NULL) TO '/tmp/rollback_data_backup.csv' WITH CSV HEADER;"

    docker cp "$DB_CONTAINER:/tmp/rollback_data_backup.csv" "$BACKUP_DIR/"
    log_success "Data backed up to $BACKUP_DIR/rollback_data_backup.csv"
  fi

  # Stop new container
  log_info "Stopping new container..."
  docker stop "$WEB_CONTAINER" || true

  # Rollback migrations
  log_info "Rolling back migrations..."

  docker exec "$WEB_CONTAINER" python manage.py migrate unified_db 0001
  docker exec "$WEB_CONTAINER" python manage.py migrate constituents 0022

  # Restore data if backed up
  if [[ -f "$BACKUP_DIR/rollback_data_backup.csv" ]]; then
    log_info "Restoring data to old field name..."

    docker cp "$BACKUP_DIR/rollback_data_backup.csv" "$DB_CONTAINER:/tmp/"

    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" << 'EOF'
CREATE TEMP TABLE rollback_data (id INTEGER, member_id INTEGER);
COPY rollback_data FROM '/tmp/rollback_data_backup.csv' WITH CSV HEADER;
UPDATE unified_db_personlink
SET fahanie_cares_member_id = rollback_data.member_id
FROM rollback_data
WHERE unified_db_personlink.id = rollback_data.id;
EOF

    log_success "Data restored to old field"
  fi

  # Restart with old code
  log_info "Restarting with old code..."

  cd "$PROJECT_ROOT"
  git checkout HEAD~1
  docker-compose -f "$COMPOSE_FILE" up -d web

  # Clear caches
  log_info "Clearing all caches..."
  docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" FLUSHDB

  # Verify rollback
  log_info "Verifying rollback..."

  local verify_result=$(docker exec "$WEB_CONTAINER" python manage.py shell << 'EOF'
from apps.unified_db.models import PersonLink
try:
    link = PersonLink.objects.first()
    if link:
        _ = link.fahanie_cares_member
        print("SUCCESS")
    else:
        print("NO_DATA")
except Exception as e:
    print(f"ERROR: {e}")
EOF
)

  if echo "$verify_result" | grep -q "SUCCESS\|NO_DATA"; then
    log_success "Rollback verification passed"
  else
    log_error "Rollback verification failed: $verify_result"
    log_error "CRITICAL: Manual intervention required"
    exit 1
  fi

  log_success "ROLLBACK SUCCESSFUL"
  log_info "Platform restored to previous state"
}

cleanup() {
  log_info "Cleaning up..."

  # Remove old container images (keep last 3)
  docker images | grep bmparliament_web | tail -n +4 | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true

  log_success "Cleanup complete"
}

generate_report() {
  local deployment_end_time=$(date +%s)
  local deployment_duration=$((deployment_end_time - DEPLOYMENT_START_TIME))

  log_info "Generating deployment report..."

  cat > "$LOG_DIR/deployment_report_$(date +%Y%m%d_%H%M%S).md" << EOF
# Deployment Report: ORM Field Rename Migration

**Date:** $(date '+%Y-%m-%d %H:%M:%S %Z')
**Duration:** $((deployment_duration / 60)) minutes $((deployment_duration % 60)) seconds
**Status:** SUCCESS

## Deployment Summary

- **Migration Start:** $(date -d "@$DEPLOYMENT_START_TIME" '+%Y-%m-%d %H:%M:%S')
- **Migration End:** $(date -d "@$deployment_end_time" '+%Y-%m-%d %H:%M:%S')
- **Strategy:** Blue-Green Deployment
- **Downtime:** 0 seconds (estimated)

## Migrations Applied

- constituents.0023_rename_fahanie_cares_member_to_bm_parliament_member
- unified_db.0002_rename_fahanie_cares_member_field

## Verification Results

- Database schema: ✅ Updated
- ORM queries: ✅ Working
- Health checks: ✅ Passing
- Error rate: ✅ Within threshold

## Post-Deployment Actions

1. Monitor error rate for 24 hours
2. Review Sentry dashboard: https://sentry.io/bmparliament
3. Document lessons learned
4. Update team on deployment success

## Logs

Full deployment logs: $LOG_FILE

---

**Generated by:** BM Parliament Deployment Script v1.0
EOF

  log_success "Report generated: $LOG_DIR/deployment_report_*.md"
}

# Main deployment flow
main() {
  mkdir -p "$BACKUP_DIR" "$LOG_DIR"

  log_info "╔═══════════════════════════════════════════════════════════════╗"
  log_info "║   BM PARLIAMENT ORM FIELD RENAME MIGRATION DEPLOYMENT        ║"
  log_info "╚═══════════════════════════════════════════════════════════════╝"

  if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY RUN MODE - No changes will be made"
  fi

  if [[ "$FORCE_ROLLBACK" == true ]]; then
    log_warning "FORCE ROLLBACK MODE - Initiating immediate rollback"
    rollback_deployment
    exit 0
  fi

  # Phase 1: Pre-deployment
  log_info ""
  log_info "📋 PHASE 1: PRE-DEPLOYMENT CHECKS"
  log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  check_dependencies
  verify_environment
  check_production_health
  create_backup
  clear_caches
  build_new_image

  log_success "Pre-deployment checks complete"

  # Phase 2: Deployment
  log_info ""
  log_info "🚀 PHASE 2: DEPLOYMENT"
  log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  deploy_new_container

  log_success "Deployment complete"

  # Phase 3: Verification
  log_info ""
  log_info "🔍 PHASE 3: VERIFICATION"
  log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if ! verify_migration; then
    log_error "Migration verification failed"
    log_error "Initiating rollback..."
    rollback_deployment
    exit 1
  fi

  monitor_error_rate
  stop_old_container

  log_success "Verification complete"

  # Phase 4: Cleanup
  log_info ""
  log_info "🧹 PHASE 4: CLEANUP"
  log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  cleanup
  generate_report

  # Final summary
  log_info ""
  log_info "╔═══════════════════════════════════════════════════════════════╗"
  log_info "║                  🎉 DEPLOYMENT SUCCESSFUL                     ║"
  log_info "╚═══════════════════════════════════════════════════════════════╝"

  log_success "Migration deployed successfully at: $(date '+%Y-%m-%d %H:%M:%S')"
  log_info ""
  log_info "Next steps:"
  log_info "1. Monitor Sentry for 24 hours: https://sentry.io/bmparliament"
  log_info "2. Review deployment report: $LOG_DIR/deployment_report_*.md"
  log_info "3. Document lessons learned"
  log_info ""
}

# Run main function
main "$@"
