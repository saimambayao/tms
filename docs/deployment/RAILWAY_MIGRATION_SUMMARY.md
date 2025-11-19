# Railway Migration Summary

This document provides a complete overview of the migration from Coolify to Railway for BM Parliament deployment.

## Migration Completed ✅

The BM Parliament application has been prepared for deployment on Railway.app, a modern cloud platform with built-in GitHub integration, automatic scaling, and managed databases.

## What Changed

### Old Setup (Coolify)
- Self-managed VPS deployment
- Manual Docker management
- Manual SSL certificate handling
- Manual scaling and resource allocation
- Custom deployment scripts

### New Setup (Railway)
- Cloud-managed platform
- Automatic Docker builds from Dockerfile
- Automatic SSL via Let's Encrypt
- Automatic scaling based on demand
- Simple TOML configuration
- GitHub CI/CD integration
- Built-in monitoring and logging

## Files Created/Modified

### Configuration Files
1. **`railway.toml`** (NEW)
   - Primary Railway configuration
   - Defines services: PostgreSQL 15, Redis 7
   - Environment variable configuration
   - Health check setup
   - **This is the main configuration file for Railway**

2. **`railway.json`** (UPDATED)
   - Legacy configuration format (keep for backward compatibility)
   - Updated to use new Dockerfile.railway
   - Includes health check configuration

3. **`deployment/docker/Dockerfile.railway`** (NEW)
   - Optimized multi-stage Dockerfile for Railway
   - Frontend build stage (Node.js)
   - Python dependencies stage
   - Production runtime stage
   - Railway-specific entrypoint script

### Documentation
1. **`docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md`** (NEW)
   - Complete Railway deployment guide
   - Environment variable reference
   - Service configuration details
   - Monitoring and troubleshooting
   - Domain and SSL setup
   - Migration guide from Coolify

2. **`CLAUDE.md`** (UPDATED)
   - Updated production deployment section
   - References to Railway instead of Coolify
   - Links to Railway configuration files
   - Environment variable references

## Getting Started with Railway

### Quick Setup
1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Railway automatically detects `railway.toml`
5. Configures PostgreSQL and Redis services
6. Builds and deploys using `Dockerfile.railway`

### Key Environment Variables
Required in Railway dashboard:
```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=[generate-new-key]
ALLOWED_HOSTS=bmparliament.gov.ph,www.bmparliament.gov.ph
```

Optional (auto-provided by Railway):
```
DATABASE_URL=postgresql://...  # Auto-provided
REDIS_URL=redis://...          # Auto-provided
PORT=8000                        # Auto-provided
```

### Deployment
Simply push to main:
```bash
git add -A
git commit -m "Your changes"
git push origin main
# Railway automatically builds and deploys
```

## Database and Cache Services

### PostgreSQL
- Version: 15 (defined in `railway.toml`)
- Database: `bmparliament_db`
- Automatically created and managed by Railway
- Connection via `DATABASE_URL` environment variable
- Automatic backups included

### Redis
- Version: 7 (defined in `railway.toml`)
- Used for caching and sessions
- Automatically created and managed by Railway
- Connection via `REDIS_URL` environment variable

## Performance Optimizations

### Dockerfile Optimizations
- **Multi-stage build**: Reduces final image size
- **Alpine base images**: Smaller footprint
- **Virtual environment**: Isolated Python dependencies
- **Non-root user**: Improved security

### Runtime Optimizations
- **Gunicorn**: 4 workers for parallel request handling
- **Worker class**: Sync (most compatible)
- **Max requests**: 1000 per worker (memory leak prevention)
- **Timeout**: 30 seconds
- **Keep-alive**: 5 seconds

### Database Optimizations
- Migrations run automatically on startup
- Database optimization command in entrypoint
- Cache table creation on startup
- Comprehensive health checks

## Monitoring and Logs

### Railway Dashboard
- Real-time application logs
- Memory and CPU usage monitoring
- Deployment history
- One-click rollback to previous versions
- Environment variable management

### Health Checks
- Health endpoint: `/health`
- Frequency: Every 30 seconds
- Timeout: 10 seconds
- Retries: 3 before restart

## Security Considerations

### Environment Variables
- All secrets stored securely in Railway dashboard
- Never committed to repository
- Auto-injected at runtime

### Container Security
- Non-root user (`appuser`)
- Minimal attack surface
- Alpine Linux base (fewer vulnerabilities)
- Regular base image updates via Railway

### Network
- HTTPS enforced for custom domains
- Automatic SSL via Let's Encrypt
- Network isolation between services

## Scaling

### Vertical Scaling
- Upgrade Railway plan for more resources
- Takes effect on next deployment

### Horizontal Scaling
- Railway handles automatic scaling
- Based on memory and CPU usage
- Load balanced across instances

## Rollback Procedure

If deployment fails:
1. Go to Railway dashboard
2. Select Web service
3. Click "Deployments" tab
4. Click "Redeploy" on previous deployment
5. Service instantly reverts

## Cost Considerations

Railway pricing:
- **Free tier**: $5 credit/month (great for development)
- **Pay-as-you-go**: Scale up as needed
- **Included**: PostgreSQL, Redis, automatic SSL
- **No surprise bills**: Caps available

Estimate for BM Parliament:
- Web service: ~$10/month
- PostgreSQL: ~$15/month
- Redis: ~$5/month
- Total: ~$30/month (production-grade)

## Migration Path from Coolify

If currently on Coolify:

1. **Backup Data**
   ```bash
   # Export PostgreSQL
   pg_dump production_db > backup.sql
   ```

2. **Create Railway Project**
   - Set up on railway.app
   - Configure environment variables
   - Connect GitHub

3. **Import Data**
   ```bash
   # In Railway PostgreSQL
   psql -d bmparliament_db < backup.sql
   ```

4. **Test Thoroughly**
   - Verify all features work
   - Check static files
   - Test user authentication
   - Verify file uploads

5. **Switch DNS**
   - Update domain CNAME to Railway
   - Wait for propagation
   - Monitor old server logs

6. **Cleanup**
   - Decommission old Coolify deployment
   - Archive old database backups

## Troubleshooting

### Common Issues

**Build fails**
- Check logs in Railway dashboard
- Ensure Dockerfile is valid
- Verify requirements.txt has all dependencies

**Application won't start**
- Review entrypoint.sh logs
- Check environment variables are set
- Verify database connection

**Static files missing**
- Collectstatic runs in entrypoint
- Check S3 configuration if using AWS
- Verify permissions on /app/staticfiles

**Slow performance**
- Check Railway resource allocation
- Monitor database query performance
- Verify Redis is connected

See `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md` for detailed troubleshooting.

## Next Steps

1. **Immediate**
   - Update environment variables in Railway dashboard
   - Test deployment on staging
   - Verify all features work

2. **Before Production**
   - Run load testing
   - Set up monitoring alerts
   - Configure backups
   - Test rollback procedure

3. **Post-Migration**
   - Monitor application logs
   - Track performance metrics
   - Gather team feedback
   - Document any issues

## References

- [Railway Documentation](https://docs.railway.app)
- [Railway GitHub Integration](https://docs.railway.app/guides/github)
- [Railway Environment Variables](https://docs.railway.app/reference/environment-variables)
- [Django Production Settings](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## Support

For Railway-specific questions:
- Railway Discord: [railway.app/support](https://railway.app)
- Railway Docs: [docs.railway.app](https://docs.railway.app)
- GitHub Issues: [Railway GitHub](https://github.com/railwayapp)

For BM Parliament-specific deployment:
- Check `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md`
- Review `CLAUDE.md` production deployment section
- Check `railway.toml` configuration

## Conclusion

The migration to Railway provides:
- ✅ Simplified deployment process
- ✅ Automatic GitHub integration
- ✅ Managed database and cache
- ✅ Automatic scaling
- ✅ Built-in monitoring
- ✅ One-click rollback
- ✅ Better cost efficiency
- ✅ Improved reliability

All configuration is in place and ready for production deployment.
