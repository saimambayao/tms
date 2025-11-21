# BM Parliament Production Dockerfile - Optimized for Railway Deployment
# Multi-stage build for optimal production container size and security

# =============================================================================
# Stage 1: Build Dependencies
# =============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy entire src directory for frontend build
COPY src/ .

# Install Node.js dependencies with verbose output for debugging
RUN npm ci --verbose || npm install

# Copy Font Awesome to static directory before building CSS
RUN mkdir -p static/fontawesome && \
    cp -r node_modules/@fortawesome/fontawesome-free/webfonts static/fontawesome/ && \
    cp node_modules/@fortawesome/fontawesome-free/css/all.min.css static/fontawesome/

# Build frontend assets
RUN npm run build-css

# =============================================================================
# Stage 2: Python Dependencies
# =============================================================================
FROM python:3.12-slim-bookworm AS python-builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel

# Copy requirements and install Python dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 3: Production Runtime
# =============================================================================
FROM python:3.12-slim-bookworm AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV DOCKER_CONTAINER=true
ENV PATH="/opt/venv/bin:$PATH"

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libopenjp2-7 \
    curl \
    wget \
    netcat-openbsd \
    gosu \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python virtual environment from builder
COPY --from=python-builder /opt/venv /opt/venv

# Set work directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/staticfiles \
    /app/media \
    /app/logs \
    /app/media/temp \
    /app/media/voter_id_photos \
    /app/media/constituents/voter_id_photos \
    /app/media/announcements \
    /app/media/documents \
    && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser src/ /app/

# Copy built frontend assets from frontend builder
COPY --from=frontend-builder --chown=appuser:appuser /app/static /app/static

# Create entrypoint script optimized for Railway
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting BM Parliament on Railway"
echo "================================================"

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    python manage.py wait_for_db
    echo "✅ Database connected"
}

# Function to run migrations
run_migrations() {
    echo "⏳ Running database migrations..."
    python manage.py migrate --noinput
    echo "✅ Migrations completed"
}

# Function to optimize database
optimize_db() {
    echo "⏳ Optimizing database..."
    python manage.py optimize_database
    echo "✅ Database optimized"
}

# Function to collect static files
collect_static() {
    echo "⏳ Collecting static files..."
    python manage.py collectstatic --noinput --clear
    echo "✅ Static files collected"
}

# Function to create cache table
create_cache() {
    echo "⏳ Creating cache table..."
    python manage.py createcachetable
    echo "✅ Cache table created"
}

# Function to setup roles
setup_roles() {
    echo "⏳ Setting up user roles..."
    python manage.py setup_roles
    echo "✅ User roles configured"
}

# Function to create superuser
create_superuser() {
    echo "⏳ Creating development superusers..."
    python manage.py create_developer_superusers
    echo "✅ Superusers created"
}

# Function to reset production stats
reset_stats() {
    if [ "$RESET_PRODUCTION_STATS" = "true" ]; then
        echo "⏳ Resetting production statistics..."
        python manage.py reset_production_stats
        echo "✅ Production statistics reset"
    fi
}


# Function to fix media permissions
fix_media_permissions() {
    echo "⏳ Setting up media directories and permissions..."
    # Ensure media directories exist (use || true to not fail on permission errors)
    mkdir -p /app/media/voter_id_photos /app/media/constituents/voter_id_photos /app/media/temp /app/media/announcements /app/media/documents 2>/dev/null || true

    # Try to set ownership (will fail if not root, but won't stop deployment)
    chown -R appuser:appuser /app/media 2>/dev/null || echo "⚠️  Could not change media ownership (volume may need manual permissions)"
    chmod -R 775 /app/media 2>/dev/null || echo "⚠️  Could not change media permissions (volume may need manual permissions)"

    chown -R appuser:appuser /app/staticfiles 2>/dev/null || true
    chmod -R 755 /app/staticfiles 2>/dev/null || true

    # Check if we can actually write to media directory
    if [ ! -w /app/media ]; then
        echo "❌ WARNING: /app/media is not writable by appuser!"
        echo "   Please configure Railway volume with: uid=1000, gid=1000, or run as root to fix permissions"
    else
        echo "✅ Media directory is writable"
    fi

    echo "✅ Media and staticfiles permissions check completed"
}

# Run deployment steps
wait_for_db
run_migrations
optimize_db
fix_media_permissions
collect_static
create_cache
setup_roles
create_superuser
reset_stats

echo "================================================"
echo "🎉 BM Parliament on Railway Ready!"
echo "================================================"

# Fix media permissions as root (Railway volume issue)
echo "⏳ Fixing media volume permissions..."
chown -R appuser:appuser /app/media 2>/dev/null || echo "⚠️  Warning: Could not change some media permissions"
chmod -R 775 /app/media 2>/dev/null || echo "⚠️  Warning: Could not change some media permissions"
echo "✅ Media permissions fixed"

# Start gunicorn as appuser with Railway-optimized settings
# Use PORT env var provided by Railway (defaults to 8000)
exec gosu appuser gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --worker-class sync --max-requests 1000 --max-requests-jitter 50 --timeout 30 --keep-alive 5 config.wsgi:application
EOF

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# NOTE: We stay as root to fix Railway volume permissions in entrypoint
# The entrypoint will drop to appuser before starting gunicorn using gosu

# Expose port (Railway will override this)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Metadata
LABEL maintainer="BM Parliament Development Team <dev@bmparliament.gov.ph>"
LABEL description="BM Parliament Production Container - Nurturing the future of the Bangsamoro"
LABEL version="1.0.0"
LABEL environment="production"
LABEL platform="railway"
