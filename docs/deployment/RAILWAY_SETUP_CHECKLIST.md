# Railway Setup Checklist

Use this checklist to set up BM Parliament on Railway.app for the first time.

## 1. Initial Setup

- [ ] Create Railway account at [railway.app](https://railway.app)
- [ ] Create new project in Railway dashboard
- [ ] Connect GitHub repository
- [ ] Authorize Railway to access GitHub

## 2. Project Configuration

- [ ] Railway auto-detects `railway.toml`
- [ ] PostgreSQL 15 service created
- [ ] Redis 7 service created
- [ ] Web service created for Django app

## 3. Environment Variables

In Railway dashboard, set these variables:

### Django Configuration
- [ ] `DJANGO_SETTINGS_MODULE` = `config.settings.production`
- [ ] `DEBUG` = `False`
- [ ] `SECRET_KEY` = [Generate new key or retrieve from secure storage]
- [ ] `ALLOWED_HOSTS` = `bmparliament.gov.ph,www.bmparliament.gov.ph`

### Optional AWS S3 (for static files)
- [ ] `USE_S3` = `True` (if using S3)
- [ ] `AWS_ACCESS_KEY_ID` = [Your AWS key]
- [ ] `AWS_SECRET_ACCESS_KEY` = [Your AWS secret]
- [ ] `AWS_STORAGE_BUCKET_NAME` = `bmparliament`
- [ ] `AWS_S3_REGION_NAME` = `ap-southeast-1`

### Email Configuration
- [ ] `EMAIL_HOST` = `smtp.gmail.com` (or your provider)
- [ ] `EMAIL_PORT` = `587`
- [ ] `EMAIL_USE_TLS` = `True`
- [ ] `EMAIL_HOST_USER` = [Your email]
- [ ] `EMAIL_HOST_PASSWORD` = [App password]
- [ ] `DEFAULT_FROM_EMAIL` = `noreply@bmparliament.gov.ph`

**Note**: Railway automatically provides:
- `DATABASE_URL` ✅
- `REDIS_URL` ✅
- `PORT` ✅

## 4. Database Configuration

- [ ] PostgreSQL service is running
- [ ] Create database: `bmparliament_db`
- [ ] Database credentials are auto-generated
- [ ] `DATABASE_URL` environment variable is set

## 5. Cache Configuration

- [ ] Redis service is running
- [ ] `REDIS_URL` environment variable is set
- [ ] Django settings configured for Redis cache

## 6. Build Verification

In Railway logs:
- [ ] Docker build starts successfully
- [ ] Frontend assets build (npm run build-css)
- [ ] Python dependencies install
- [ ] Image successfully builds

## 7. Deployment Verification

In Railway logs during startup:
- [ ] Database connection successful
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Cache table created
- [ ] User roles set up
- [ ] Gunicorn server starts
- [ ] Health checks pass

## 8. Domain Configuration

- [ ] Add custom domain in Railway settings
- [ ] Get Railway CNAME value
- [ ] Update DNS provider (Route53, GoDaddy, etc.)
- [ ] Point domain to Railway CNAME
- [ ] Wait for DNS propagation (5-30 minutes)
- [ ] Verify HTTPS certificate created
- [ ] Test domain in browser

## 9. Testing

### Basic Functionality
- [ ] Homepage loads (bmparliament.gov.ph)
- [ ] Login page works
- [ ] Can create admin user
- [ ] Database queries work
- [ ] Static files load (CSS, JS, images)

### Features
- [ ] User registration works
- [ ] Constituent search works
- [ ] File uploads work
- [ ] Email notifications send
- [ ] Admin panel accessible
- [ ] API endpoints respond

### Performance
- [ ] Page loads in < 2 seconds
- [ ] Admin panel responsive
- [ ] No console errors
- [ ] Mobile version works

## 10. Monitoring Setup

- [ ] Enable Railway logs
- [ ] Set up log alerts (optional)
- [ ] Monitor CPU usage
- [ ] Monitor memory usage
- [ ] Check database connections
- [ ] Verify auto-scaling works

## 11. Backup Configuration

- [ ] PostgreSQL automatic backups enabled
- [ ] Backup retention set (30 days recommended)
- [ ] Test backup restore procedure
- [ ] Document backup location

## 12. SSL/HTTPS Verification

- [ ] SSL certificate auto-created by Let's Encrypt
- [ ] HTTPS enforced for custom domain
- [ ] Browser shows secure lock icon
- [ ] No SSL warnings in console

## 13. DNS and CDN (Optional)

- [ ] CloudFront distribution configured (if using)
- [ ] CloudFront points to Railway domain
- [ ] Static files cached (if using S3)
- [ ] Cache invalidation working

## 14. Documentation

- [ ] Read `RAILWAY_MIGRATION_SUMMARY.md`
- [ ] Read `RAILWAY_DEPLOYMENT_GUIDE.md`
- [ ] Review `railway.toml` configuration
- [ ] Bookmark Railway dashboard URL
- [ ] Save emergency contacts

## 15. Production Checklist

### Before Going Live
- [ ] All tests pass locally
- [ ] All environment variables set
- [ ] Database backup taken
- [ ] Staging environment tested
- [ ] Rollback procedure tested
- [ ] Team trained on new platform

### Cutover Day
- [ ] Notify users of maintenance window
- [ ] Verify all services healthy on Railway
- [ ] Update DNS to point to Railway
- [ ] Monitor logs for errors
- [ ] Have rollback plan ready
- [ ] Notify team when live

## 16. Post-Launch

- [ ] Monitor application logs daily
- [ ] Check error rates
- [ ] Verify database performance
- [ ] Review autoscaling behavior
- [ ] Collect team feedback
- [ ] Document any issues
- [ ] Plan optimizations

## Helpful Commands

### View logs
```
Railway Dashboard → Web Service → Logs
```

### Check deployment status
```
Railway Dashboard → Web Service → Deployments
```

### Restart service
```
Railway Dashboard → Web Service → Restart
```

### View environment variables
```
Railway Dashboard → Web Service → Variables
```

### SSH into container (if needed)
```
Railway CLI: railway shell
```

## Emergency Procedures

### If deployment fails
1. Check build logs in Railway dashboard
2. Verify environment variables
3. Check Dockerfile syntax
4. Review requirements.txt
5. Rollback to previous deployment

### If site goes down
1. Check Railway status page
2. View application logs
3. Check database connection
4. Verify environment variables
5. Restart service
6. Rollback if needed

### If database has issues
1. Check database logs in Railway
2. Verify connection pool settings
3. Check query performance
4. Review recent migrations
5. Consider scaling up

## Support Resources

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Support**: [railway.app/support](https://railway.app)
- **GitHub Issues**: [railway issues](https://github.com/railwayapp/issues)
- **BM Parliament Docs**: See `/docs/deployment/`

## Sign-Off

- [ ] Deployment team lead: _________________ Date: _______
- [ ] Project manager: _________________ Date: _______
- [ ] System administrator: _________________ Date: _______

---

**Notes**: Add any additional notes, known issues, or custom configurations below:

```
[Space for notes]
```
