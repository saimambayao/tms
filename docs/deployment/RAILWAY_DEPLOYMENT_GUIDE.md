# Railway Deployment Guide

BM Parliament is now deployed on Railway.app, a modern cloud platform that provides container orchestration, managed databases, and CI/CD integration.

## Quick Start

### 1. Connect Your Repository
1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Click "Deploy from GitHub"
4. Select the BM Parliament repository

### 2. Add Services
Railway will automatically detect the configuration from `railway.toml` and create:
- **Web Service**: Django application
- **PostgreSQL Database**: Primary data store
- **Redis Cache**: Caching and session management

### 3. Configure Environment Variables
Railway automatically provides:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `PORT`: Application port (defaults to 8000)

Add these additional variables in Railway dashboard:

```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=[your-secret-key-here]
ALLOWED_HOSTS=bmparliament.gov.ph,www.bmparliament.gov.ph
```

### 4. Deploy
Push to main branch, Railway automatically builds and deploys using the Dockerfile.

## Configuration Files

### `railway.toml`
Primary configuration file (recommended):
- Defines build process (Dockerfile)
- Sets up environment variables
- Configures services (PostgreSQL, Redis)
- Health check configuration

### `railway.json` (Legacy)
Alternative configuration format - `railway.toml` is preferred.

### `Dockerfile.railway`
Optimized multi-stage Dockerfile for Railway:
- Stage 1: Frontend assets build (Node.js)
- Stage 2: Python dependencies
- Stage 3: Production runtime

## Required Environment Variables

### Django Configuration
```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False (always False in production)
SECRET_KEY=[generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())']
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Database Configuration
Railway automatically provides `DATABASE_URL`. If you need to override:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=bmparliament_db (from railway.toml)
DB_USER=postgres (from Railway)
DB_HOST=provided-by-railway
DB_PORT=5432
DB_PASSWORD=provided-by-railway
```

### Cache Configuration
Railway provides `REDIS_URL` automatically. Django settings will auto-detect.

### Email Configuration
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com (or your email provider)
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@bmparliament.gov.ph
```

### AWS S3 (for static files and media - optional)
```
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=bmparliament
AWS_S3_REGION_NAME=ap-southeast-1
AWS_S3_CUSTOM_DOMAIN=your-cloudfront-url.cloudfront.net
AWS_QUERYSTRING_AUTH=False
```

## Service Configuration

### PostgreSQL Database
- Version: 15 (defined in railway.toml)
- Database: `bmparliament_db`
- Automatically created by Railway
- Connection string: `DATABASE_URL` environment variable

### Redis Cache
- Version: 7 (defined in railway.toml)
- Purpose: Caching, sessions, Celery tasks
- Connection string: `REDIS_URL` environment variable

### Web Service
- Runs `deployment/docker/Dockerfile.railway`
- Start command: `sh /app/entrypoint.sh`
- Exposes port: 8000 (Railway maps to public URL)
- Health checks: Every 30 seconds to `/health` endpoint

## Deployment Process

### Build Phase
1. Railway clones repository
2. Builds Docker image using `Dockerfile.railway`
3. Multi-stage build optimizes image size
4. Image pushed to Railway registry

### Startup Phase (Entrypoint)
The `entrypoint.sh` script:
1. Waits for database to be ready
2. Runs database migrations
3. Optimizes database
4. Collects static files
5. Creates cache table
6. Sets up user roles
7. Creates superuser (if needed)
8. Warms application cache
9. Starts Gunicorn server

### Running Phase
- Gunicorn listens on `PORT` environment variable (8000)
- Health checks verify application is responsive
- Failed health checks trigger automatic restarts
- Logs available in Railway dashboard

## Monitoring and Logs

### View Logs
In Railway dashboard:
1. Go to your project
2. Select Web service
3. Click "Logs" tab
4. Real-time logs from application

### Common Issues

**Database Connection Errors**
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL service is running
- Check network policies allow connection

**Static Files Missing**
- Ensure `collectstatic` runs in entrypoint
- Check S3 configuration if using AWS

**Redis Connection Errors**
- Verify Redis service is running
- Check `REDIS_URL` environment variable
- Ensure settings use correct cache backend

**Out of Memory**
- Railway provides 512MB free tier
- Monitor memory usage in dashboard
- Upgrade to paid tier for more resources

## Scaling

### Vertical Scaling
Upgrade Railway plan for more memory/CPU:
1. Go to project settings
2. Upgrade plan
3. Restart services

### Horizontal Scaling
Railway handles automatic scaling:
- Observes memory and CPU usage
- Automatically spins up replicas if needed
- Load balanced across instances

## Domain Configuration

### Connect Custom Domain
1. In Railway dashboard, go to project settings
2. Click "Custom Domain"
3. Add `bmparliament.gov.ph`
4. Railway provides CNAME to point DNS to
5. Update DNS provider (e.g., GoDaddy, Route53)

### SSL/TLS
- Railway automatically provides SSL with Let's Encrypt
- Certificates auto-renew
- HTTPS enforced for custom domains

## CI/CD Pipeline

### Automatic Deployment
- Every push to `main` branch triggers build
- Building happens on Railway infrastructure
- Automatic deployment on successful build

### Manual Deployment
1. Go to Railway dashboard
2. Select Web service
3. Click "Deploy" button
4. Choose commit to deploy

### Rollback
1. Go to deployments history
2. Click "Redeploy" on previous deployment
3. Service instantly reverts to previous version

## Scheduled Tasks (Optional)

If using Celery for background tasks:

1. Add Celery Worker service:
```toml
[services.worker]
type = "worker"
command = "celery -A config worker -l info"
```

2. Set same environment variables as web service
3. Connect to same Redis and PostgreSQL services

## Troubleshooting

### Application Won't Start
1. Check logs in Railway dashboard
2. Verify all environment variables are set
3. Check `entrypoint.sh` doesn't have permission issues
4. Ensure Dockerfile builds locally first

### Slow Performance
1. Check Railway resource allocation
2. Monitor database query performance
3. Verify Redis is properly configured
4. Check network latency

### Deployment Fails
1. Review build logs in Railway
2. Ensure Dockerfile is valid
3. Check for missing dependencies in requirements.txt
4. Verify `railway.toml` syntax

## Migration from Coolify

If migrating from Coolify:
1. Export data from Coolify PostgreSQL
2. Import into Railway PostgreSQL
3. Update DNS to point to Railway
4. Verify all environment variables are set
5. Test thoroughly before cutover

## References

- [Railway Documentation](https://docs.railway.app)
- [Railway Environment Variables](https://docs.railway.app/reference/environment-variables)
- [Railway GitHub Integration](https://docs.railway.app/guides/github)
- [Django Production Settings](https://docs.djangoproject.com/en/5.0/howto/deployment/)
