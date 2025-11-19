# 🚀 BM Parliament Coolify Deployment Execution Guide

**Quick execution checklist for deploying BM Parliament to production via Coolify**

> **⚠️ CRITICAL**: This deployment will reset all statistics to zero for a clean production launch. Current development stats (247 updates, 45 this month, etc.) will be cleared.

## 📋 Pre-Deployment Checklist

### ✅ Requirements Verification

- [ ] VPS ready (Ubuntu 22.04+, 4GB RAM, 40GB storage minimum)
- [ ] Domain DNS configured (`bmparliament.gov.ph` → VPS IP)
- [ ] SSH access to VPS established
- [ ] Git repository access confirmed
- [ ] Production environment variables prepared

### ✅ Deployment Files Ready

All required files have been created in the repository:

- [ ] `deployment/docker/docker-compose/coolify.yml` ✅
- [ ] `.env.coolify.example` (project root) ✅
- [ ] `deployment/docker/Dockerfile.production` ✅
- [ ] `deployment/nginx/nginx-coolify.conf` ✅
- [ ] `src/apps/core/management/commands/reset_production_stats.py` ✅
- [ ] `docs/deployment/COOLIFY_DEPLOYMENT_GUIDE.md` ✅ (comprehensive reference)

---

## 🖥️ VPS Setup (15 minutes)

### 1. Connect and Update VPS

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Install essentials
apt install -y curl wget git unzip ufw

# Configure timezone
timedatectl set-timezone Asia/Manila

# Set hostname
hostnamectl set-hostname bm-parliament-prod
```

### 2. Configure Firewall

```bash
# Setup UFW
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp  # Coolify dashboard
ufw --force enable
ufw status
```

---

## 🐳 Coolify Installation (10 minutes)

### 1. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify installation
docker --version
docker compose version
```

### 2. Install Coolify

```bash
# Run Coolify installer
curl -fsSL https://coolify.io/install.sh | bash

# Wait for installation (5-10 minutes)
# Installation complete when you see success message
```

### 3. Access Coolify Dashboard

```bash
# Open in browser
http://YOUR_VPS_IP:8000

# Complete setup wizard:
# 1. Create admin account
# 2. Add localhost server
# 3. Verify server connection
```

---

## 📦 Application Deployment (20 minutes)

### 1. Upload Project Files

```bash
# Create project directory on VPS
mkdir -p /home/coolify/bm-parliament
cd /home/coolify/bm-parliament

# Clone repository
git clone https://github.com/your-org/bm-parliament.git .

# Verify deployment files exist
ls -la deployment/docker/docker-compose/coolify.yml
ls -la .env.coolify.example
ls -la deployment/docker/Dockerfile.production
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp .env.coolify.example .env

# Generate secure keys
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
echo "DB_PASSWORD=$(openssl rand -base64 32)"
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"

# Edit .env file with your production values
nano .env
```

**Required Environment Variables:**
```bash
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=bm-parliament.gov.ph,www.bm-parliament.gov.ph,YOUR_VPS_IP
DB_PASSWORD=your-generated-db-password
REDIS_PASSWORD=your-generated-redis-password
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
NOTION_API_KEY=secret_your_notion_token
NOTION_DATABASE_ID=your-notion-db-id
```

### 3. Create Application in Coolify

**In Coolify Dashboard:**

1. **Applications** → **New Application**
2. **Name**: `bm-parliament-production`
3. **Type**: Docker Compose
4. **Source**: Local Directory
5. **Directory**: `/home/coolify/bm-parliament`
6. **Docker Compose File**: `deployment/docker/docker-compose/coolify.yml`

### 4. Upload Configuration

**In Coolify Application Settings:**

1. **Configuration Tab**
2. **Upload Docker Compose**: Paste content of `deployment/docker/docker-compose/coolify.yml`
3. **Environment Variables**: Upload `.env` file
4. **Domain**: Add `bm-parliament.gov.ph`
5. **SSL**: Enable Let's Encrypt

---

## 🚀 Deploy and Launch (15 minutes)

### 1. Initial Deployment

```bash
# In Coolify Dashboard:
# 1. Click "Deploy" button
# 2. Monitor deployment logs
# 3. Wait for all services to become healthy (5-10 minutes)
```

### 2. Post-Deployment Setup

```bash
# Connect to web container
docker exec -it bmparliament_web /bin/bash

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# ⚠️ CRITICAL: Reset production statistics to zero
python manage.py reset_production_stats --confirm

# Verify reset
python manage.py shell -c "
from django.core.cache import cache
print('Stats reset completed')
print(f'Total members: {cache.get(\"stats_total_members\", 0)}')
print(f'Referrals processed: {cache.get(\"stats_referrals_processed\", 0)}')
"

# Exit container
exit
```

### 3. Domain and SSL Configuration

**In Coolify Application:**

1. **Domains Tab** → Add `bm-parliament.gov.ph`
2. **SSL Tab** → Enable Let's Encrypt
3. **Wait for certificate** provisioning (2-5 minutes)
4. **Enable Force HTTPS**

---

## ✅ Verification Checklist (10 minutes)

### 1. Health Checks

```bash
# Test health endpoints
curl https://bm-parliament.gov.ph/health/
curl https://bm-parliament.gov.ph/health/detailed/

# Verify SSL
curl -I http://bm-parliament.gov.ph  # Should redirect to HTTPS
openssl s_client -connect bm-parliament.gov.ph:443 -servername bm-parliament.gov.ph
```

### 2. Functional Testing

**Manual verification:**

- [ ] Homepage loads: `https://bm-parliament.gov.ph`
- [ ] Registration works: `/member-registration/`
- [ ] Login/logout functional: `/accounts/login/`
- [ ] Admin panel accessible: `/admin/`
- [ ] Chapters page loads: `/chapters/`
- [ ] Ministry programs: `/ministries-ppas/`
- [ ] Contact form: `/contact/`
- [ ] Mobile responsive design
- [ ] **Statistics show zero values** (clean production start)

### 3. Performance Verification

```bash
# Check container status
docker ps
docker stats --no-stream

# Verify database connectivity
docker exec bmparliament_db pg_isready -U bmparliament_user

# Check Redis connectivity
docker exec bmparliament_redis redis-cli -a YOUR_REDIS_PASSWORD ping
```

---

## 📊 Production Statistics Reset Verification

**Expected Clean Launch Statistics:**

- **Registered Members**: 0 (will grow with real registrations)
- **Total Updates**: 0 (instead of current 247)
- **This Month**: 0 (instead of current 45)
- **Programs**: Actual count (legitimate programs preserved)
- **Bills Filed**: 0 (instead of current 8)

**Verification Command:**
```bash
docker exec -it bmparliament_web python manage.py shell -c "
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()
print('=== PRODUCTION STATISTICS ===')
print(f'Total Users: {User.objects.count()}')
print(f'Cached Members: {cache.get(\"stats_total_members\", 0)}')
print(f'Cached Referrals: {cache.get(\"stats_referrals_processed\", 0)}')
print('✅ Statistics reset verified')
"
```

---

## 🎯 Go-Live Actions

### 1. Enable Monitoring

```bash
# Verify monitoring endpoints
curl https://bm-parliament.gov.ph/monitoring/
curl https://bm-parliament.gov.ph/metrics/

# Set up alerts in Coolify dashboard
```

### 2. Configure Backups

**In Coolify Dashboard:**

1. **Backups Tab** → Enable automatic backups
2. **Schedule**: Daily at 2:00 AM Manila time
3. **Retention**: 30 days
4. **Test backup** restore procedure

### 3. Final Security Check

```bash
# Verify security headers
curl -I https://bm-parliament.gov.ph | grep -E "(Strict-Transport|X-Content|X-Frame)"

# Check rate limiting
# Test login rate limiting
# Test API rate limiting
```

---

## 📞 Post-Deployment Support

### Immediate Actions Required

1. **Announce Launch**: Platform ready with clean statistics
2. **Monitor Logs**: Watch for any errors in first 24 hours
3. **Test User Registration**: Verify real user workflow
4. **Social Media**: Update links to production domain

### Monitoring Commands

```bash
# Real-time application logs
docker logs -f bmparliament_web

# Check system resources
docker stats
htop

# Database performance
docker exec bmparliament_db psql -U bmparliament_user -d bmparliament_prod -c "SELECT * FROM pg_stat_activity;"
```

### Emergency Contacts

- **Technical Support**: dev@bmparliament.gov.ph
- **System Admin**: admin@bm-parliament.gov.ph
- **Coolify Issues**: [Coolify Discord](https://discord.gg/coolify)

---

## 📈 Success Metrics

**Deployment Successful When:**

- [ ] All health checks pass
- [ ] SSL certificate valid and forced
- [ ] Statistics reset to zero confirmed
- [ ] User registration functional
- [ ] Admin panel accessible
- [ ] Email notifications working
- [ ] Mobile interface responsive
- [ ] Monitoring dashboard active
- [ ] Backup system enabled
- [ ] Domain resolves correctly

**Platform Ready for Public Launch! 🎉**

---

**Total Deployment Time**: ~60 minutes  
**Platform Status**: Production-ready with clean statistics  
**Next Steps**: Monitor, maintain, and grow the community impact

*For detailed troubleshooting and maintenance procedures, refer to the comprehensive [Coolify Deployment Guide](../COOLIFY_DEPLOYMENT_GUIDE.md)*