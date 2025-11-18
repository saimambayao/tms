# Docker Setup for FahanieCares

This guide provides instructions for running the FahanieCares Django application using Docker.

## Prerequisites

- Docker Desktop installed on your machine
- Docker Compose installed (usually comes with Docker Desktop)
- Git for cloning the repository

## Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/your-org/fahanie-cares.git
   cd fahanie-cares
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your configuration values, especially:
   - `SECRET_KEY` (generate a secure key for production)
   - `NOTION_API_KEY` (required for Notion integration)
   - Database credentials if different from defaults

3. **Build and start the services**:
   ```bash
   # For development
   docker-compose up --build

   # For production
   docker-compose -f deployment/docker/docker-compose/production.yml up --build
   ```

4. **Access the application**:
   - Development: http://localhost:3000
   - Production: http://localhost:80

## Development Setup

### Running in Development Mode

```bash
# Start all services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Accessing Services

- **Django Application**: http://localhost:3000
- **PostgreSQL Database**: localhost:5432
- **Redis**: localhost:6379
- **Nginx (optional)**: http://localhost:80

### Running Django Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Access Django shell
docker-compose exec web python manage.py shell_plus
```

### Development Tips

1. **Hot Reload**: The development setup includes volume mounting, so code changes are reflected immediately without rebuilding.

2. **Database Management**:
   ```bash
   # Access PostgreSQL
   docker-compose exec db psql -U fahaniecares_user -d fahaniecares_db
   ```

3. **Redis CLI**:
   ```bash
   docker-compose exec redis redis-cli
   ```

## Production Setup

### Building for Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### Production Configuration

1. **SSL/TLS Setup**:
   - Place SSL certificates in `deployment/ssl/`
   - Update nginx configuration with your domain

2. **Environment Variables**:
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure proper `ALLOWED_HOSTS`
   - Set production database credentials

3. **Static Files**:
   - Static files are served by Nginx in production
   - Run `collectstatic` during deployment

### Production Commands

```bash
# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery=3

# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U fahaniecares_user fahaniecares_db > backup.sql
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Find process using port
   lsof -i :3000
   # Kill process
   kill -9 <PID>
   ```

2. **Database Connection Failed**:
   - Ensure database service is healthy: `docker-compose ps`
   - Check logs: `docker-compose logs db`

3. **Permission Errors**:
   - Ensure proper file permissions
   - Run: `chmod +x deployment/entrypoint.sh`

4. **Static Files Not Loading**:
   - Run collectstatic: `docker-compose exec web python manage.py collectstatic --noinput`

### Debugging

```bash
# Access container shell
docker-compose exec web /bin/bash

# View all containers
docker ps -a

# Inspect container
docker inspect fahaniecares_web

# Remove all containers and volumes (WARNING: deletes data)
docker-compose down -v
```

## Maintenance

### Updating Dependencies

1. Update `requirements.txt`
2. Rebuild images: `docker-compose build --no-cache`
3. Restart services: `docker-compose up -d`

### Database Migrations

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

### Monitoring

- Application logs: `docker-compose logs -f web`
- Nginx logs: `docker-compose logs -f nginx`
- Database logs: `docker-compose logs -f db`
- Redis logs: `docker-compose logs -f redis`

## Security Notes

1. **Never commit `.env` files** with real credentials
2. **Use secrets management** in production (e.g., Docker Secrets, AWS Secrets Manager)
3. **Regularly update** base images and dependencies
4. **Enable** firewall rules to restrict access
5. **Use** HTTPS in production with valid SSL certificates

## Testing Environment

### Running Tests with Docker

The project includes dedicated testing infrastructure:

```bash
# Run comprehensive test suite
docker-compose -f docker-compose.test.yml up test_runner

# Run performance tests
docker-compose -f docker-compose.test.yml up performance_test

# Run both test suites
docker-compose -f docker-compose.test.yml up
```

### Test Services

1. **test_runner**: Runs unit, integration, and E2E tests
   - Includes test coverage reporting
   - Generates HTML coverage reports
   - Uses isolated test database

2. **performance_test**: Runs performance benchmarks
   - Tests application performance under load
   - Generates performance reports

### Test Reports

Test reports are stored in Docker volumes:
- **Test Coverage**: `fahaniecares_test_reports` volume
- **Performance Reports**: `fahaniecares_performance_reports` volume

```bash
# Access test coverage reports
docker run --rm -v fahaniecares_test_reports:/reports alpine ls -la /reports

# Access performance reports
docker run --rm -v fahaniecares_performance_reports:/reports alpine ls -la /reports
```

## Docker Compose Files

The project includes multiple Docker Compose configurations:

- **docker-compose.yml**: Development environment (port 3000)
- **docker-compose.prod.yml**: Production environment with Nginx (port 80/443)
- **docker-compose.test.yml**: Testing environment with isolated services

## Environment Configuration

### Development (.env)
```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
DB_HOST=db
REDIS_URL=redis://redis:6379/0
```

### Production (.env)
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Testing (.env)
```bash
TESTING=True
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend
DB_NAME=fahaniecares_test_db
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Nginx Documentation](https://nginx.org/en/docs/)