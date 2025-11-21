# Railway Volumes Setup for Media Files

This guide shows you how to set up **Railway Volumes** for persistent media file storage (user uploads, images, documents) - all within Railway, no external services needed!

## Why Railway Volumes?

Railway uses **ephemeral storage** by default - files uploaded to your container are deleted when you redeploy. Railway Volumes provide:

- ✅ **Persistent storage** that survives deployments
- ✅ **No extra cost** beyond Railway subscription
- ✅ **Simple setup** - just a few clicks in Railway dashboard
- ✅ **No external services** - everything in Railway
- ⚠️ **Small downtime** during redeployments (seconds, not minutes)

## Pricing

Railway Volumes are included in your Railway plan:
- **Hobby Plan**: $5/month includes 100GB storage
- **Pro Plan**: $20/month includes 100GB storage
- **Additional storage**: $0.25/GB/month if you need more than 100GB

For most small-medium apps, the included 100GB is more than enough!

---

## Setup Steps (5 minutes)

### Step 1: Create Volume in Railway Dashboard

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your project**: `protective-happiness` (or your project name)
3. **Click on your web service**
4. **Go to "Volumes" tab** (in the left sidebar)
5. **Click "New Volume"**:
   - **Mount Path**: `/data`
   - **Size**: Leave default (will use included storage)
   - Click **Add**

6. **Wait for deployment**: Railway will redeploy your service with the volume attached

### Step 2: Add Environment Variable

1. **Still in your web service**, go to **Variables** tab
2. **Add new variable**:
   ```
   RAILWAY_VOLUME_MOUNT_PATH=/data
   ```
3. **Click Add**
4. Railway will automatically redeploy

### Step 3: Update Nginx Configuration (if using custom nginx)

If you're using a custom nginx configuration, ensure it serves media files:

```nginx
location /media/ {
    alias /data/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

## How It Works

### Django Configuration (Already Done!)

Your Django settings at `src/config/settings/base.py` are already configured:

```python
# Railway Volumes: When deployed on Railway with a volume mounted at /data,
# media files will be stored persistently on the volume
RAILWAY_VOLUME_MOUNT = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', None)

if RAILWAY_VOLUME_MOUNT:
    # Use Railway Volume for persistent media storage
    MEDIA_ROOT = os.path.join(RAILWAY_VOLUME_MOUNT, 'media')
    MEDIA_URL = '/media/'
else:
    # Local development: use project directory
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
```

**What this does**:
- **Local development**: Files stored in `src/media/` (not persistent, for testing only)
- **Railway with volume**: Files stored in `/data/media/` (persistent across deployments)

### File Structure on Railway

```
/app/                          # Your Django app (ephemeral)
  ├── manage.py
  ├── apps/
  └── ...

/data/                         # Railway Volume (persistent)
  └── media/                   # User uploads stored here
      ├── profile_photos/
      ├── documents/
      ├── certificates/
      └── ...
```

---

## Testing the Setup

### 1. Check Volume is Mounted

In Railway console or logs, run:
```bash
railway run bash
ls -la /data
```

You should see the `/data` directory exists.

### 2. Test File Upload

1. **Login to admin**: https://bmparliament.gov.ph/admin
2. **Upload a test image** (e.g., user profile photo)
3. **Check if file persists**:
   - Upload the file
   - Go to Railway dashboard → Click **Restart**
   - After restart, check if the image is still there ✅

### 3. Django Shell Test

```bash
# In Railway console
railway run python manage.py shell

# Test media storage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

# Check media root
from django.conf import settings
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
# Should print: /data/media

# Upload test file
path = default_storage.save('test.txt', ContentFile(b'Hello Railway Volumes!'))
print(f"File saved to: {path}")

# Check file exists
print(f"File exists: {default_storage.exists(path)}")
```

---

## Important: Deployment Downtime

⚠️ **Railway Volumes have a small limitation**: During redeployments, there's a few seconds of downtime because the volume can only be mounted to one instance at a time.

**What this means**:
- ✅ Normal operation: No issues, files persist
- ⚠️ During deployment: 5-10 seconds where site is unavailable
- ✅ After deployment: Site back online with all files intact

**Mitigation strategies**:
1. Deploy during low-traffic hours
2. Add a deployment notification to users
3. If you need zero downtime, consider AWS S3 instead (but that requires external service)

---

## Managing Storage

### Check Volume Usage

1. **Railway Dashboard** → Your Service → **Volumes** tab
2. View storage usage and capacity

### Increase Storage (if needed)

1. **Railway Dashboard** → Your Service → **Volumes** tab
2. Click on your volume
3. Increase size (charges $0.25/GB/month for storage beyond included 100GB)

### Backup Volume Data

Currently, Railway doesn't have automatic backups for volumes. To backup:

```bash
# In Railway console
railway run bash

# Create backup
cd /data
tar -czf backup-$(date +%Y%m%d).tar.gz media/

# Download backup (you'll need to set up a way to transfer this file)
```

**Better approach**: Implement automated backups to S3 (optional):
```python
# Django management command to backup media to S3
python manage.py backup_media_to_s3
```

---

## Troubleshooting

### Files not persisting after deployment

**Check**:
1. Volume is created and mounted at `/data`
2. Environment variable `RAILWAY_VOLUME_MOUNT_PATH=/data` is set
3. Django settings shows `MEDIA_ROOT=/data/media` (check in Railway logs)

**Fix**:
```bash
railway run python manage.py shell
from django.conf import settings
print(settings.MEDIA_ROOT)  # Should be /data/media
```

### "Permission denied" when uploading files

**Fix**: Ensure volume has correct permissions
```bash
railway run bash
chmod -R 755 /data/media
chown -R railway:railway /data/media  # Railway user
```

### Volume full

**Fix**:
1. Check what's using space: `du -sh /data/media/*`
2. Clean up old files
3. Increase volume size in Railway dashboard

---

## Migration from Local Storage

If you already have media files stored locally (before using volumes):

```bash
# 1. Download existing media files from Railway
railway run bash
cd /app/media
tar -czf media-backup.tar.gz .

# 2. Upload to volume
railway run bash
cd /data
mkdir -p media
cd media
# Upload your media-backup.tar.gz here
tar -xzf media-backup.tar.gz
rm media-backup.tar.gz
```

---

## Comparison: Railway Volumes vs AWS S3

| Feature | Railway Volumes | AWS S3 |
|---------|----------------|--------|
| **Setup** | 2 clicks | ~30 mins setup |
| **Cost** | Included in plan | ~$0.50/month |
| **Extra Services** | None | AWS account needed |
| **Downtime** | Few seconds during deploy | Zero downtime |
| **Global CDN** | No (single region) | Yes (CloudFront) |
| **Backup** | Manual | Automated |
| **Best For** | Small-medium apps | Large apps, global users |

**Recommendation**:
- **Railway Volumes**: Perfect for most apps, simple, no extra cost
- **AWS S3**: Only if you need global CDN or zero-downtime deployments

---

## Summary

✅ **Setup Complete!**

Your Django app is now configured to use Railway Volumes:

1. **What's configured in code**:
   - ✅ Django settings updated to use `/data/media/` when volume is mounted
   - ✅ Automatic fallback to local storage for development
   - ✅ URL configuration already serves media files

2. **What you need to do in Railway**:
   - 🔲 Create volume with mount path `/data`
   - 🔲 Add environment variable `RAILWAY_VOLUME_MOUNT_PATH=/data`
   - 🔲 Test file upload

**Next Steps**:
1. Go to Railway Dashboard
2. Create volume at `/data`
3. Add environment variable
4. Wait for redeploy
5. Test upload! 🎉

---

## Support

- **Railway Volumes Docs**: https://docs.railway.app/reference/volumes
- **Railway Discord**: https://discord.gg/railway (for help)
- **Your Project**: https://railway.app/project/protective-happiness
