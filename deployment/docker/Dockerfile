# Multi-stage Dockerfile for FahanieCares Django Application

# Stage 1: Base builder with system dependencies
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements file
COPY src/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Development stage
FROM python:3.11-slim AS development

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Set work directory
WORKDIR /app

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
COPY src/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

# Copy project files
COPY --chown=django:django src/ .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.development

# Expose port
EXPOSE 3000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]

# Stage 3: Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Set work directory
WORKDIR /app

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
COPY src/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/* && \
    pip install gunicorn

# Copy project files
COPY --chown=django:django src/ .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles /var/log/nginx /var/log/supervisor && \
    chown -R django:django /app && \
    chown -R django:django /var/log/nginx

# Copy nginx and supervisor configs
COPY deployment/nginx/nginx.conf /etc/nginx/nginx.conf
COPY deployment/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Expose ports
EXPOSE 8000 80

# Run with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]