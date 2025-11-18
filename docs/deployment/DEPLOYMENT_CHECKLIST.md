# #FahanieCares Production Deployment Checklist

## ✅ Pre-Deployment Checklist

### 🔧 Infrastructure Setup
- [ ] VPS provisioned with minimum 4GB RAM, 2 vCPU, 40GB SSD
- [ ] Ubuntu 22.04 LTS installed and updated
- [ ] Domain `fahaniecares.ph` pointing to VPS IP address
- [ ] DNS records configured (A records for @ and www)
- [ ] Coolify installed and configured on VPS
- [ ] SSL certificates configured (Let's Encrypt via Coolify)

### 🔐 Security Configuration
- [ ] Strong passwords generated for all services:
  - [ ] `DJANGO_SECRET_KEY` (generated with Django utility)
  - [ ] `POSTGRES_PASSWORD` (32+ character random string)
  - [ ] `REDIS_PASSWORD` (32+ character random string)
- [ ] Environment variables configured in Coolify
- [ ] HTTPS enforcement enabled
- [ ] Security headers configured
- [ ] Rate limiting configured

### 📊 Database and Services
- [ ] PostgreSQL 15 container deployed
- [ ] Redis 7 container deployed  
- [ ] Database health checks passing
- [ ] Cache connectivity verified

### 🔗 External Integrations
- [ ] Notion API integration token configured
- [ ] Notion database IDs set up
- [ ] SMTP email service configured
- [ ] AWS S3 configured (optional)
- [ ] Sentry error tracking configured (optional)

### 📱 Application Configuration
- [ ] Docker Compose configuration tested
- [ ] Production settings verified
- [ ] Static files configuration tested
- [ ] Media files storage configured

## 🚀 Deployment Steps

### 1. Repository Preparation
```bash
# Ensure all files are committed
git add .
git commit -m "feat: production deployment configuration"
git push origin main
```

### 2. Coolify Application Creation
- [ ] Create new project in Coolify
- [ ] Add Docker Compose application
- [ ] Set repository URL and branch (main)
- [ ] Configure build settings
- [ ] Set Docker Compose file path: `deployment/docker/docker-compose/coolify.yml`

### 3. Environment Variables Setup
Copy variables from `.env.coolify.example` and configure:

#### Core Settings
- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] `DJANGO_SECRET_KEY`
- [ ] `ALLOWED_HOSTS`
- [ ] `CSRF_TRUSTED_ORIGINS`
- [ ] `SERVICE_FQDN_WEB`

#### Database Configuration  
- [ ] `POSTGRES_DB`
- [ ] `POSTGRES_USER`
- [ ] `POSTGRES_PASSWORD`

#### Cache Configuration
- [ ] `REDIS_PASSWORD`

#### Security Settings
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`

#### External Services
- [ ] `NOTION_API_KEY`
- [ ] `NOTION_DATABASE_ID`
- [ ] Email configuration
- [ ] AWS S3 (if using cloud storage)
- [ ] Sentry (if using error tracking)

### 4. Domain and SSL Configuration
- [ ] Configure primary domain: `fahaniecares.ph`
- [ ] Configure www redirect: `www.fahaniecares.ph`
- [ ] Enable Let's Encrypt SSL
- [ ] Enable HTTPS redirect
- [ ] Verify SSL certificate installation

### 5. Initial Deployment
- [ ] Deploy application from Coolify dashboard
- [ ] Monitor deployment logs
- [ ] Verify all containers start successfully
- [ ] Check health endpoints

## 🗂️ Post-Deployment Configuration

### 1. Database Setup
```bash
# Access the web container
docker exec -it fahaniecares_web bash

# Run database migrations
python manage.py migrate

# Create cache table
python manage.py createcachetable

# Setup RBAC permissions
python manage.py setup_rbac

# Create superuser account
python manage.py createsuperuser
```

### 2. Static Files and Assets
```bash
# Collect static files
python manage.py collectstatic --noinput --clear

# Optimize database
python manage.py optimize_database
```

### 3. Production Data Reset
```bash
# Reset all sample data for clean production launch
python manage.py reset_production_stats --confirm --preserve-superusers
```

This command will:
- ✅ Remove all test registrations and constituents
- ✅ Clear all sample referrals and updates
- ✅ Reset chapter memberships to zero
- ✅ Clear form submissions and communications
- ✅ Reset impact statistics to start from zero
- ⭐ Preserve system configuration and superuser accounts

### 4. Verify Application Health
- [ ] Check health endpoint: `https://fahaniecares.ph/health/`
- [ ] Verify database connectivity
- [ ] Test Redis cache functionality
- [ ] Confirm all static files loading
- [ ] Test user registration flow
- [ ] Verify email sending functionality

## 🔍 Testing and Verification

### 1. Functional Testing
- [ ] Home page loads correctly with zero statistics
- [ ] User registration works
- [ ] Login/logout functionality
- [ ] Contact forms submit successfully
- [ ] Email notifications send
- [ ] Admin panel accessible
- [ ] Service request flow works

### 2. Performance Testing
- [ ] Page load times < 3 seconds
- [ ] Database queries optimized
- [ ] Static files cached properly
- [ ] CDN configured (if applicable)

### 3. Security Testing
- [ ] HTTPS enforced on all pages
- [ ] Security headers present
- [ ] No sensitive data exposed
- [ ] Rate limiting functional
- [ ] CSRF protection active (all forms working without 403 errors)
- [ ] DJANGO_SETTINGS_MODULE environment variable verified

### 4. Mobile and Accessibility
- [ ] Mobile responsive design works
- [ ] Progressive Web App features
- [ ] Accessibility compliance
- [ ] Font Awesome icons loading

## 📊 Monitoring Setup

### 1. Health Monitoring
- [ ] `/health/` endpoint responding
- [ ] `/health/detailed/` providing system status
- [ ] `/ready/` endpoint for readiness checks
- [ ] `/metrics/` endpoint for monitoring data

### 2. Error Tracking
- [ ] Sentry configured for error tracking
- [ ] Log aggregation set up
- [ ] Performance monitoring active
- [ ] Uptime monitoring configured

### 3. Backup Strategy
- [ ] Database backup schedule configured
- [ ] Media files backup configured
- [ ] Configuration backup documented
- [ ] Recovery procedures tested

## 🔄 Maintenance Procedures

### 1. Regular Updates
```bash
# Update application code
git pull origin main
# Redeploy from Coolify dashboard

# Update system packages
sudo apt update && sudo apt upgrade

# Update Docker images (via Coolify)
```

### 2. Database Maintenance
```bash
# Database optimization (weekly)
python manage.py optimize_database

# Check for migration issues
python manage.py showmigrations

# Database cleanup (monthly)
python manage.py clearsessions
```

### 3. Log Management
```bash
# View application logs
docker logs fahaniecares_web

# View all service logs
docker-compose -f deployment/docker/docker-compose/coolify.yml logs

# Rotate logs (configure logrotate)
```

## 🚨 Emergency Procedures

### 1. Application Issues
- [ ] Check Coolify dashboard for service status
- [ ] Review application logs
- [ ] Verify environment variables
- [ ] Check database connectivity
- [ ] Restart services if needed

### 2. Database Issues
- [ ] Check PostgreSQL container status
- [ ] Verify database credentials
- [ ] Check disk space
- [ ] Review database logs
- [ ] Restore from backup if needed

### 3. Performance Issues
- [ ] Monitor resource usage
- [ ] Check for memory leaks
- [ ] Review slow queries
- [ ] Scale resources if needed
- [ ] Optimize cache usage

## 📞 Contact Information

### Technical Support
- **Infrastructure**: VPS Provider Support
- **Domain Issues**: Domain Registrar Support
- **Application Issues**: Development Team
- **Monitoring**: Sentry/Monitoring Service

### Emergency Contacts
- **Primary**: [Primary Technical Contact]
- **Secondary**: [Secondary Technical Contact]
- **Infrastructure**: [VPS Provider Emergency]

---

## ✅ Deployment Completion

Once all checklist items are completed:

1. **Application Status**: ✅ Deployed and healthy
2. **Database Status**: ✅ Migrated and optimized
3. **Security Status**: ✅ HTTPS and headers configured
4. **Monitoring Status**: ✅ Health checks and error tracking active
5. **Performance Status**: ✅ Optimized and caching enabled
6. **Data Status**: ✅ Clean production environment with zero sample data

**🎉 #FahanieCares is now live and ready to serve the Bangsamoro community!**

The platform is ready to receive real registrations, service requests, and community engagement. All statistics will grow organically from zero as real users interact with the system.

---

**#FahanieCares Development Team**  
*Bringing Bangsamoro Public Service Closer to You*