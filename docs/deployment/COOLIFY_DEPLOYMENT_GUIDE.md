# 🚀 #FahanieCares Coolify Deployment Guide

Complete step-by-step guide for deploying the #FahanieCares platform on a VPS using Coolify.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [VPS Setup](#vps-setup)
3. [Coolify Installation](#coolify-installation)
4. [Domain Configuration](#domain-configuration)
5. [Application Deployment](#application-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Database Setup](#database-setup)
8. [Production Launch](#production-launch)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### VPS Requirements

**Minimum Specifications:**
- **CPU**: 2 vCPUs
- **RAM**: 4GB
- **Storage**: 40GB SSD
- **OS**: Ubuntu 22.04 LTS or 24.04 LTS
- **Network**: Public IP with ports 80, 443, 22 open

**Recommended Specifications:**
- **CPU**: 4 vCPUs
- **RAM**: 8GB
- **Storage**: 80GB SSD
- **Bandwidth**: 1TB+ monthly transfer

### Local Requirements

- Git installed
- SSH client
- Domain name (e.g., `fahaniecares.gov.ph`)
- SSL certificate (or use Coolify's automatic Let's Encrypt)

---

## 🖥️ VPS Setup

### 1. Initial Server Configuration

Connect to your VPS via SSH:

```bash
ssh root@your-vps-ip
```

### 2. Update System Packages

```bash
# Update package list
apt update && apt upgrade -y

# Install essential packages
apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Configure timezone
timedatectl set-timezone Asia/Manila

# Set hostname
hostnamectl set-hostname fahaniecares-prod
```

### 3. Configure Firewall

```bash
# Install and configure UFW
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Check firewall status
ufw status
```

### 4. Create Non-Root User (Optional but Recommended)

```bash
# Create user
adduser coolify
usermod -aG sudo coolify

# Switch to new user
su - coolify
```

---

## 🐳 Coolify Installation

### 1. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker compose version
```

### 2. Install Coolify

```bash
# Download and run Coolify installer
curl -fsSL https://coolify.io/install.sh | bash

# Wait for installation to complete (this may take 5-10 minutes)
```

### 3. Access Coolify Web Interface

1. Open browser and navigate to: `http://your-vps-ip:8000`
2. Complete the initial setup wizard
3. Create your admin account
4. Set up your first server (localhost)

---

## 🌐 Domain Configuration

### 1. DNS Setup

Configure your domain's DNS records:

```bash
# A Records
fahaniecares.gov.ph     A    your-vps-ip
www.fahaniecares.gov.ph A    your-vps-ip

# Optional: CNAME for subdomains
api.fahaniecares.gov.ph CNAME fahaniecares.gov.ph
```

### 2. SSL Certificate Configuration

**Option A: Automatic (Recommended)**
- Coolify will automatically provision Let's Encrypt certificates
- Enable "Force HTTPS" in Coolify application settings

**Option B: Custom Certificate**
- Upload your certificate files in Coolify
- Configure SSL in the application settings

---

## 📦 Application Deployment

### 1. Create New Application in Coolify

1. **Navigate to Applications** in Coolify dashboard
2. **Click "New Application"**
3. **Choose "Docker Compose"** as deployment type
4. **Configure basic settings:**
   - Name: `fahaniecares-production`
   - Description: `#FahanieCares Public Service Platform`
   - Environment: `production`

### 2. Upload Docker Configuration

**Upload these files to your server:**

```bash
# Create project directory
mkdir -p /home/coolify/fahaniecares
cd /home/coolify/fahaniecares

# Clone repository (or upload files)
git clone https://github.com/your-org/fahanie-cares.git .

# Copy Coolify-specific files
cp deployment/docker/docker-compose/coolify.yml docker-compose.yml
cp .env.example .env
```

### 3. Configure Docker Compose in Coolify

In Coolify dashboard:

1. **Go to your application**
2. **Select "Configuration" tab**
3. **Upload or paste your `docker-compose.yml` content**
4. **Set build context** to `src/`

---

## ⚙️ Environment Configuration

### 1. Environment Variables

Copy and configure the `.env` file:

```bash
cd /home/coolify/fahaniecares
cp .env.coolify.example .env
```

### 2. Required Environment Variables

**Essential Configuration:**

```bash
# Django Core
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
ALLOWED_HOSTS=fahaniecares.gov.ph,www.fahaniecares.gov.ph,your-vps-ip
CSRF_TRUSTED_ORIGINS=https://fahaniecares.gov.ph,https://www.fahaniecares.gov.ph

# Database
DB_NAME=fahaniecares_prod
DB_USER=fahaniecares_user
DB_PASSWORD=your-super-strong-database-password

# Redis
REDIS_PASSWORD=your-super-strong-redis-password

# Email (Example with Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=#FahanieCares <noreply@fahaniecares.gov.ph>

# Notion API
NOTION_API_KEY=secret_your_notion_integration_token_here
NOTION_DATABASE_ID=your-notion-database-id-here

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### 3. Generate Secure Keys

```bash
# Generate Django SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"

# Generate database password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 32
```

### 4. Configure in Coolify

1. **Go to Environment Variables** section in Coolify
2. **Upload your `.env` file** or manually add variables
3. **Mark sensitive variables** as "Secret" in Coolify

---

## 🗄️ Database Setup

### 1. PostgreSQL Configuration

The Docker Compose configuration includes PostgreSQL setup. Coolify will:

1. **Create PostgreSQL container** with persistent storage
2. **Initialize database** with configured credentials
3. **Set up health checks** for database connectivity

### 2. Initial Database Migration

After deployment, run initial setup:

```bash
# Connect to web container
docker exec -it fahaniecares_web /bin/bash

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Reset production stats (clean launch)
python manage.py reset_production_stats --confirm

# Exit container
exit
```

---

## 🚀 Production Launch

### 1. Deploy Application

In Coolify dashboard:

1. **Click "Deploy"** button
2. **Monitor deployment logs** for any errors
3. **Wait for all services** to become healthy
4. **Verify deployment** at your domain

### 2. Post-Deployment Verification

**Check Health Endpoints:**

```bash
# Health check
curl https://fahaniecares.gov.ph/health/

# Detailed health check
curl https://fahaniecares.gov.ph/health/detailed/

# Metrics endpoint
curl https://fahaniecares.gov.ph/metrics/
```

**Verify SSL:**

```bash
# Check SSL certificate
openssl s_client -connect fahaniecares.gov.ph:443 -servername fahaniecares.gov.ph

# Test HTTPS redirect
curl -I http://fahaniecares.gov.ph
```

### 3. Reset Production Statistics

Ensure clean launch with zero statistics:

```bash
# Access Django shell
docker exec -it fahaniecares_web python manage.py shell

# Or run the reset command
docker exec -it fahaniecares_web python manage.py reset_production_stats --confirm
```

### 4. Test Core Functionality

**Manual Testing Checklist:**

- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] Login/logout functionality
- [ ] Chapter directory displays
- [ ] Ministry programs load
- [ ] Contact form submission
- [ ] Admin panel access
- [ ] Mobile responsiveness
- [ ] SSL certificate valid
- [ ] Error pages display properly

---

## 📊 Monitoring & Maintenance

### 1. Coolify Monitoring

Coolify provides built-in monitoring:

- **Resource usage** (CPU, Memory, Disk)
- **Container health** status
- **Application logs** and metrics
- **Deployment history** and rollbacks

### 2. Application Monitoring

**Built-in Monitoring URLs:**

```bash
# Monitoring dashboard
https://fahaniecares.gov.ph/monitoring/

# Health check
https://fahaniecares.gov.ph/health/

# System metrics
https://fahaniecares.gov.ph/metrics/
```

### 3. Log Management

**Access logs through Coolify or direct container access:**

```bash
# Application logs
docker logs fahaniecares_web

# Database logs
docker logs fahaniecares_db

# Redis logs  
docker logs fahaniecares_redis

# Nginx logs (if using Nginx service)
docker logs fahaniecares_nginx

# Celery logs
docker logs fahaniecares_celery

# Follow logs in real-time
docker logs -f fahaniecares_web
```

### 4. Automated Backups

**Set up automated backups using Coolify's backup feature:**

1. **Configure backup schedule** in Coolify
2. **Set backup retention** policy
3. **Test backup restoration** procedure

**Manual backup commands:**

```bash
# Database backup
docker exec fahaniecares_db_prod pg_dump -U fahaniecares_user fahaniecares_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Application data backup
docker exec fahaniecares_web_prod python manage.py dumpdata > app_data_$(date +%Y%m%d_%H%M%S).json
```

### 5. Security Updates

**Regular maintenance schedule:**

```bash
# Update system packages (monthly)
sudo apt update && sudo apt upgrade -y

# Update Docker images (weekly)
docker compose pull && docker compose up -d

# Monitor security advisories
# Subscribe to Django security announcements
# Monitor Coolify updates
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start

**Check container logs:**

```bash
docker logs fahaniecares_web
docker compose logs web
```

**Common causes:**
- Missing environment variables (especially `DJANGO_SETTINGS_MODULE`)
- Database connection failure
- Static file collection errors
- Port conflicts
- CSRF configuration issues

**Solutions:**
```bash
# Rebuild containers
docker compose down && docker compose up --build -d

# Check environment variables
docker exec fahaniecares_web env | grep DJANGO

# Verify DJANGO_SETTINGS_MODULE is set
docker exec fahaniecares_web env | grep DJANGO_SETTINGS_MODULE

# Verify database connectivity
docker exec fahaniecares_web python manage.py dbshell
```

#### 2. Database Connection Issues

**Check database container:**

```bash
docker logs fahaniecares_db
docker exec fahaniecares_db pg_isready -U fahaniecares_user
```

**Solutions:**
```bash
# Restart database container
docker restart fahaniecares_db

# Check database credentials
docker exec fahaniecares_db psql -U fahaniecares_user -d fahaniecares_production -c "SELECT 1;"
```

#### 3. SSL Certificate Problems

**Check certificate status:**

```bash
# Verify certificate in Coolify dashboard
# Check Let's Encrypt logs
# Ensure domain DNS is correctly configured
```

**Solutions:**
```bash
# Force certificate renewal in Coolify
# Verify domain ownership
# Check firewall settings for ports 80/443
```

#### 4. CSRF Verification Failed (Forms Return 403 Error)

**Symptoms:**
- All forms return "CSRF verification failed. Request aborted" 
- Login page returns 403 Forbidden error
- Contact forms and registration fail

**Root Cause:**
- Missing or incorrect `DJANGO_SETTINGS_MODULE` environment variable
- Incorrect `CSRF_TRUSTED_ORIGINS` configuration
- Using base Django settings instead of production settings

**Check CSRF Configuration:**
```bash
# Verify DJANGO_SETTINGS_MODULE is set correctly
docker exec fahaniecares_web env | grep DJANGO_SETTINGS_MODULE

# Should output: DJANGO_SETTINGS_MODULE=config.settings.production

# Check if production settings are being loaded
docker exec fahaniecares_web python manage.py shell -c "
from django.conf import settings
print('CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
"
```

**Solutions:**
```bash
# 1. Ensure DJANGO_SETTINGS_MODULE is set in environment variables
# Add to your .env file or Coolify environment variables:
DJANGO_SETTINGS_MODULE=config.settings.production

# 2. Verify CSRF_TRUSTED_ORIGINS includes your domain
# Should include: https://fahaniecares.ph, https://www.fahaniecares.ph

# 3. Restart containers after environment variable changes
docker compose down && docker compose up -d

# 4. Test CSRF configuration
curl -I https://fahaniecares.ph/accounts/login/
# Should return 200 OK, not 403 Forbidden
```

**Prevention:**
- Always include `DJANGO_SETTINGS_MODULE=config.settings.production` in production deployments
- Test forms after deployment to ensure CSRF protection is working correctly
- Monitor application logs for CSRF-related errors

#### 5. High Memory Usage

**Monitor resource usage:**

```bash
docker stats
htop
```

**Solutions:**
```bash
# Optimize Gunicorn workers
export GUNICORN_WORKERS=2

# Enable memory limits in docker-compose.yml
# Clear application cache
docker exec fahaniecares_web python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

#### 6. Slow Performance

**Performance diagnostics:**

```bash
# Check database performance
docker exec fahaniecares_db psql -U fahaniecares_user -d fahaniecares_production -c "SELECT * FROM pg_stat_activity;"

# Monitor Redis performance
docker exec fahaniecares_redis redis-cli -a ${REDIS_PASSWORD} INFO stats

# Check disk space
df -h
```

**Optimization:**
```bash
# Optimize database
docker exec fahaniecares_web python manage.py optimize_database

# Clear cache
docker exec fahaniecares_redis redis-cli -a ${REDIS_PASSWORD} FLUSHALL

# Restart services
docker compose restart
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] VPS meets minimum requirements
- [ ] Domain DNS configured correctly
- [ ] SSL certificate ready (or Let's Encrypt enabled)
- [ ] Environment variables configured (including DJANGO_SETTINGS_MODULE)
- [ ] DJANGO_SETTINGS_MODULE=config.settings.production set
- [ ] CSRF_TRUSTED_ORIGINS configured for your domain
- [ ] Database credentials generated
- [ ] Email SMTP configured
- [ ] Notion API integration set up

### During Deployment

- [ ] Coolify successfully installed
- [ ] Docker Compose configuration uploaded
- [ ] Environment variables set in Coolify
- [ ] Application deployed without errors
- [ ] All containers healthy
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] DJANGO_SETTINGS_MODULE environment variable verified
- [ ] CSRF configuration tested (forms working)

### Post-Deployment

- [ ] Health endpoints responding
- [ ] SSL certificate valid
- [ ] Domain resolves correctly
- [ ] User registration working
- [ ] Email notifications functional
- [ ] Admin panel accessible
- [ ] Production statistics reset
- [ ] Monitoring configured
- [ ] Backup system enabled

---

## 📞 Support and Resources

### Documentation

- [Coolify Official Documentation](https://coolify.io/docs)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Community Support

- [Coolify Discord Community](https://discord.gg/coolify)
- [#FahanieCares Development Team](mailto:dev@fahaniecares.gov.ph)

### Emergency Contacts

- **Technical Support**: dev@fahaniecares.gov.ph
- **System Administrator**: admin@fahaniecares.gov.ph
- **Emergency Hotline**: +63 xxx xxx xxxx

---

## 🎉 Conclusion

Your #FahanieCares platform is now successfully deployed on Coolify! The platform features:

✅ **Production-ready infrastructure** with PostgreSQL, Redis, and Nginx  
✅ **Automatic SSL certificates** and security headers  
✅ **Comprehensive monitoring** and health checks  
✅ **Clean production statistics** starting from zero  
✅ **Scalable architecture** ready for community growth  
✅ **Professional security** meeting government standards  

The platform is ready to serve the Bangsamoro community with reliable, secure, and efficient public services.

**🚀 Welcome to production! Bringing Public Service Closer to You.**

---

*Last updated: June 2025*  
*#FahanieCares Development Team*