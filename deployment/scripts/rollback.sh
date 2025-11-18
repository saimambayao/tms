#!/bin/bash

# #FahanieCares Website Rollback Script

set -e

# Configuration
APP_NAME="fahaniecares"
APP_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "#FahanieCares Website Rollback"
echo "============================================"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}Error: Backup directory not found${NC}"
    exit 1
fi

# List available backups
echo -e "${YELLOW}Available backups:${NC}"
ls -la $BACKUP_DIR/backup_*.tar.gz | sort -r | head -10

# Get the latest backup or specific backup
if [ -z "$1" ]; then
    BACKUP_FILE=$(ls -t $BACKUP_DIR/backup_*.tar.gz | head -1)
    echo -e "${YELLOW}Using latest backup: $BACKUP_FILE${NC}"
else
    BACKUP_FILE="$BACKUP_DIR/$1"
    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
        exit 1
    fi
fi

# Confirm rollback
echo -e "${YELLOW}This will rollback to: $BACKUP_FILE${NC}"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled."
    exit 0
fi

# Create temporary backup of current state
echo -e "${YELLOW}Creating backup of current state...${NC}"
TEMP_BACKUP="$BACKUP_DIR/temp_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$TEMP_BACKUP" -C "$APP_DIR" .

# Stop services
echo -e "${YELLOW}Stopping services...${NC}"
sudo systemctl stop gunicorn_$APP_NAME
sudo systemctl stop celery_$APP_NAME || true
sudo systemctl stop celerybeat_$APP_NAME || true

# Clear current application directory
echo -e "${YELLOW}Clearing application directory...${NC}"
rm -rf $APP_DIR/*

# Extract backup
echo -e "${YELLOW}Extracting backup...${NC}"
tar -xzf "$BACKUP_FILE" -C "$APP_DIR"

# Restore permissions
echo -e "${YELLOW}Restoring permissions...${NC}"
chown -R www-data:www-data $APP_DIR

# Activate virtual environment
cd $APP_DIR
source venv/bin/activate

# Install dependencies (in case they changed)
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Run migrations (rollback if needed)
echo -e "${YELLOW}Running migrations...${NC}"
python manage.py migrate

# Start services
echo -e "${YELLOW}Starting services...${NC}"
sudo systemctl start gunicorn_$APP_NAME
sudo systemctl start nginx
sudo systemctl start celery_$APP_NAME || true
sudo systemctl start celerybeat_$APP_NAME || true

# Verify rollback
echo -e "${YELLOW}Verifying rollback...${NC}"
curl -f http://localhost/health/ || echo -e "${RED}Warning: Health check failed${NC}"

# Success message
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Rollback completed successfully!${NC}"
echo -e "${GREEN}Rolled back to: $BACKUP_FILE${NC}"
echo -e "${GREEN}Temporary backup of previous state: $TEMP_BACKUP${NC}"
echo -e "${GREEN}============================================${NC}"