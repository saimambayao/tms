#!/bin/bash
set -e

echo "🚀 Starting #FahanieCares Production Server"
echo "================================================"

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    python manage.py wait_for_db
    echo "✅ Database connected"
}

# Function to build CSS if needed
build_css() {
    if [ -f "package.json" ] && [ -d "node_modules" ]; then
        echo "⏳ Building CSS with TailwindCSS..."
        npm run build-css
        echo "✅ CSS built successfully"
    else
        echo "⚠️  Skipping CSS build (no Node.js environment found)"
    fi
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
    python manage.py optimize_database || echo "⚠️  Database optimization skipped"
    echo "✅ Database optimization attempted"
}

# Function to collect static files
collect_static() {
    echo "⏳ Collecting static files..."
    # Add version info to static files
    echo "/* Version: ${STATIC_VERSION:-unknown} - Built: $(date -u) */" > static/css/build-info.css
    python manage.py collectstatic --noinput --clear
    echo "✅ Static files collected"
}

# Function to create cache table
create_cache() {
    echo "⏳ Creating cache table..."
    python manage.py createcachetable || echo "⚠️  Cache table exists"
    echo "✅ Cache table ready"
}

# Function to setup roles
setup_roles() {
    echo "⏳ Setting up user roles..."
    python manage.py setup_roles || echo "⚠️  Roles already configured"
    echo "✅ User roles configured"
}

# Function to invalidate CDN cache
invalidate_cdn() {
    if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        echo "⏳ Invalidating CloudFront cache..."
        python manage.py invalidate_cdn_cache --wait || echo "⚠️  Cache invalidation failed"
        echo "✅ CDN cache invalidated"
    else
        echo "ℹ️  Skipping CDN invalidation (no distribution ID)"
    fi
}

# Main execution
echo "📦 Static Version: ${STATIC_VERSION:-not set}"
echo "🌍 Environment: Production"
echo "================================================"

# Run all startup tasks
wait_for_db
build_css
run_migrations
optimize_db
collect_static
create_cache
setup_roles
invalidate_cdn

echo "================================================"
echo "🎉 #FahanieCares Production Server Ready!"
echo "================================================"

# Start Gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class ${GUNICORN_WORKER_CLASS:-sync} \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --timeout ${GUNICORN_TIMEOUT:-30} \
    --keep-alive ${GUNICORN_KEEPALIVE:-5}