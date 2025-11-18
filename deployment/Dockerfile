FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
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

# Install Python dependencies
COPY src/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY src/ /app/

# Copy entrypoint script
COPY deployment/entrypoint-production.sh /app/entrypoint.sh

# Create media directories with proper permissions
RUN mkdir -p /app/media /app/logs /app/staticfiles
RUN mkdir -p /app/media/announcements /app/media/documents /app/media/constituents /app/media/voter_id_photos

# Create user to run the application and set permissions
RUN useradd -m -u 1000 appuser
RUN chmod +x /app/entrypoint.sh
RUN chown -R appuser:appuser /app

# Collect static files as root (before switching user)
RUN python manage.py collectstatic --noinput

# Set entrypoint (will handle user switching)
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application
# Production: port 8000, Development: port 3000 (override with docker run -p 3000:3000)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]

EXPOSE 8000
EXPOSE 3000