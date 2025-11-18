# 🚀 PRODUCTION CSS FIX - DO THIS NOW

## Option 1: ONE COMMAND (Recommended) - 30 seconds

SSH to your production server and paste this:

```bash
curl -s https://raw.githubusercontent.com/tech-bangsamoro/fahanie-cares/main/deploy-css-fix.sh | bash
```

**That's it!** The script will automatically:
- ✅ Pull latest code
- ✅ Find your Docker container
- ✅ Rebuild CSS
- ✅ Deploy static files
- ✅ Clear CloudFront cache
- ✅ Show colored progress

## Option 2: Manual Steps - 2 minutes

If the automated script fails, run these manually:

```bash
# 1. Pull latest code
cd /path/to/fahanie-cares
git pull origin main

# 2. Find your container
docker ps | grep web

# 3. Rebuild CSS (replace CONTAINER_NAME)
docker exec CONTAINER_NAME npm run build-css
docker exec CONTAINER_NAME python manage.py collectstatic --noinput

# 4. Clear CloudFront (if you have AWS CLI)
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Option 3: GitHub Actions - 1 click

1. Go to: https://github.com/tech-bangsamoro/fahanie-cares/actions
2. Click "Deploy CSS Fix to Production"
3. Click "Run workflow"
4. Click green "Run workflow" button

(Requires GitHub Actions secrets to be configured)

## Verification

After deployment:
1. Wait 2-5 minutes for CloudFront
2. Open https://fahaniecares.ph
3. Hard refresh: **Ctrl+F5** (Windows) or **Cmd+Shift+R** (Mac)
4. Check navbar dropdown - should be scrollable now!

## Troubleshooting

If navbar still not scrollable:
- Clear browser cache completely
- Try incognito/private mode
- Check browser console for errors (F12)
- Wait 5 more minutes for CloudFront

---

**Need help?** The issue is that CloudFront CDN is caching old CSS. The fix rebuilds CSS and clears the cache.