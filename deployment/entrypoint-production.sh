#!/bin/bash

# Production entrypoint script for #FahanieCares Django application

set -e

echo "Starting #FahanieCares production deployment..."

# Check if running as root (needed for permission fixes)
if [ "$(id -u)" = "0" ]; then
    echo "Running as root - fixing media directory permissions..."
    
    # Create media directories as root
    mkdir -p /app/media/announcements
    mkdir -p /app/media/documents  
    mkdir -p /app/media/constituents
    mkdir -p /app/media/voter_id_photos
    mkdir -p /app/media/constituents/voter_id_photos  # Additional path for voter ID photos
    mkdir -p /app/media/temp  # Temporary upload directory
    mkdir -p /app/logs
    
    # Fix ownership and permissions for media directories
    chown -R 1000:1000 /app/media
    chown -R 1000:1000 /app/logs
    chmod -R 755 /app/media
    chmod -R 755 /app/logs
    
    echo "Switching to appuser..."
    # Switch to appuser and re-run this script
    exec su appuser -c "$0 $@"
else
    echo "Running as appuser - ensuring directories exist..."
    
    # Create directories if they don't exist (as appuser)
    mkdir -p /app/media/announcements 2>/dev/null || echo "Media directories already exist"
    mkdir -p /app/media/documents 2>/dev/null || echo "Documents directory already exists"
    mkdir -p /app/media/constituents 2>/dev/null || echo "Constituents directory already exists"
    mkdir -p /app/media/voter_id_photos 2>/dev/null || echo "Voter ID photos directory already exists"
    mkdir -p /app/media/constituents/voter_id_photos 2>/dev/null || echo "Constituents voter ID photos directory already exists"
    mkdir -p /app/media/temp 2>/dev/null || echo "Temp directory already exists"
    mkdir -p /app/logs 2>/dev/null || echo "Logs directory already exists"
fi

# Wait for database to be ready
echo "Waiting for database..."
python manage.py wait_for_db

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create cache table if using database cache
echo "Creating cache table..."
python manage.py createcachetable 2>/dev/null || echo "Cache table already exists"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (development/testing)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser..."
    python manage.py create_superuser || echo "Superuser already exists"
fi

# Setup roles and permissions
echo "Setting up roles and permissions..."
python manage.py setup_rbac || echo "RBAC setup completed"

# Grant developer and system admin access
echo "Granting developer and system admin access..."
python /app/src/grant_developer_admin_access.py

echo "#FahanieCares production setup completed successfully!"

# Start the application
exec "$@"
