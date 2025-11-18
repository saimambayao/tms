#!/bin/sh

set -e

echo "Starting FahanieCares application..."

# Change to Django project directory
cd /app

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create cache table
echo "Creating cache table..."
python manage.py createcachetable || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (only in development)
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.development" ]; then
    echo "Creating superuser (if not exists)..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fahaniecares.ph', 'admin123')
    print('Superuser created!')
else:
    print('Superuser already exists.')
" || true
fi

# Setup roles and permissions
echo "Setting up roles and permissions..."
python manage.py setup_roles || true
python manage.py setup_rbac || true

# Start the application
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    echo "Starting Gunicorn server..."
    exec gunicorn config.wsgi:application \
        --name fahaniecares \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class gevent \
        --worker-connections 1000 \
        --max-requests 5000 \
        --max-requests-jitter 500 \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --enable-stdio-inheritance \
        --preload
else
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:3000
fi