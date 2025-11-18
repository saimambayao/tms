# Registration Fix Deployment Guide

## Summary of Fixes

This deployment addresses critical registration issues reported on https://fahaniecares.ph/accounts/register/

### 1. Radio Button Form Submission Fix
**Issue**: Radio button values were not being submitted with the form due to incorrect name attribute.
**Fix**: Updated `simple_radio_group.html` to use `field.html_name` instead of `field.name`
```html
<!-- Before -->
<input type="radio" name="{{ field.name }}" ...>

<!-- After -->
<input type="radio" name="{{ field.html_name }}" ...>
```

### 2. Enhanced Radio Button Visual Feedback
**Issue**: Users reported radio buttons were "slow and clicking them cannot be distinguished right away"
**Fix**: Added CSS animations, hover effects, and immediate visual feedback
- Smooth transitions on hover and selection
- Scale animation on click
- Better contrast and visibility
- Touch device optimizations

### 3. Media Upload Directory Issues
**Issue**: Voter ID photo uploads failing due to missing directories or permissions
**Fix**: Enhanced `entrypoint-production.sh` to create all necessary directories:
```bash
mkdir -p /app/media/voter_id_photos
mkdir -p /app/media/constituents/voter_id_photos  # Fallback path
mkdir -p /app/media/temp  # Temporary uploads
```

### 4. File Upload Resilience
**Issue**: Single point of failure if primary upload directory creation fails
**Fix**: Implemented fallback logic in `utils.py`:
- Tries multiple directory paths in order
- Logs all attempts for debugging
- Falls back gracefully if all paths fail

## Deployment Instructions

### Prerequisites
- SSH access to production server
- Docker and docker-compose installed
- Git repository access

### Method 1: Using the Deployment Script

1. **Copy the deployment script to production server**:
```bash
scp deploy-registration-fixes.sh user@production-server:/path/to/fahanie-cares/
```

2. **SSH into production server**:
```bash
ssh user@production-server
cd /path/to/fahanie-cares
```

3. **Run the deployment script**:
```bash
./deploy-registration-fixes.sh
```

### Method 2: Manual Deployment Steps

1. **Pull latest changes**:
```bash
git pull origin main
```

2. **Build Docker image**:
```bash
docker-compose build web
```

3. **Run migrations**:
```bash
docker-compose exec web python manage.py migrate
```

4. **Fix media permissions**:
```bash
docker-compose exec web python manage.py fix_media_permissions
```

5. **Collect static files**:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

6. **Restart services**:
```bash
docker-compose restart web
```

## Verification Steps

### 1. Check Service Status
```bash
docker-compose ps
```
All services should show as "Up"

### 2. Monitor Logs
```bash
docker-compose logs -f web | grep -i "registration\|member"
```

### 3. Test Registration Form
1. Navigate to https://fahaniecares.ph/accounts/register/
2. Fill out the form completely
3. Verify:
   - Radio buttons show immediate visual feedback
   - Radio buttons maintain selection after clicks
   - File upload accepts voter ID photos
   - Form submits successfully

### 4. Check Database
```bash
docker-compose exec web python manage.py shell
```
```python
from apps.constituents.models import FahanieCaresMember
# Check recent registrations
recent = FahanieCaresMember.objects.order_by('-created_at')[:5]
for member in recent:
    print(f"{member.user.username} - {member.created_at} - Sector: {member.sector}")
```

## Rollback Procedure

If issues occur after deployment:

1. **Revert to previous version**:
```bash
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>
docker-compose build web
docker-compose restart web
```

2. **Check logs for errors**:
```bash
docker-compose logs --tail=100 web
```

## Monitoring Post-Deployment

### Key Metrics to Watch
1. **Registration Success Rate**: Monitor completed registrations vs attempts
2. **Error Logs**: Watch for file upload errors or form validation issues
3. **Performance**: Check response times for registration page
4. **User Feedback**: Monitor support channels for user reports

### Log Locations
- Django logs: `docker-compose logs web`
- Nginx logs: `docker-compose logs nginx`
- Database logs: `docker-compose logs db`

## Support Contacts

If issues persist after deployment:
1. Check Docker logs for detailed error messages
2. Review `/media/` directory permissions
3. Verify database connectivity
4. Contact development team with error details

## Success Criteria

The deployment is successful when:
- ✅ Registration form loads without errors
- ✅ Radio buttons show visual feedback immediately
- ✅ All radio button selections are preserved on form errors
- ✅ Voter ID photos upload successfully
- ✅ New registrations appear in the database
- ✅ No increase in error logs

---

**Last Updated**: June 10, 2025
**Commit**: 7aa63691 (Radio, Image, and other fixes)