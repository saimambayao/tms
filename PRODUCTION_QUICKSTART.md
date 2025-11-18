# Production CSS Fix - Quick Start Guide

## 🚀 Immediate Fix (Copy & Paste)

SSH to your production server and run:

```bash
# Option 1: If your container is named 'fahanie-cares-web-1'
docker exec fahanie-cares-web-1 npm run build-css
docker exec fahanie-cares-web-1 python manage.py collectstatic --noinput

# Option 2: Find container name first
docker ps | grep web
# Then use the container name from above
docker exec [CONTAINER_NAME] npm run build-css
docker exec [CONTAINER_NAME] python manage.py collectstatic --noinput
```

## 🔄 Clear CloudFront Cache

### If you have AWS CLI configured:
```bash
# Find your distribution ID (if you don't know it)
aws cloudfront list-distributions --query "DistributionList.Items[?contains(Aliases.Items || [''], 'fahaniecares.ph')].Id" --output text

# Clear cache (replace E1234567890ABC with your ID)
aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"
```

### If you DON'T have AWS CLI:
1. Go to [AWS Console](https://console.aws.amazon.com/cloudfront)
2. Click on your distribution
3. Go to "Invalidations" tab
4. Click "Create Invalidation"
5. Enter `/*` in the paths field
6. Click "Create"

## ✅ Verification

After 5-10 minutes:
1. Open https://fahaniecares.ph
2. Hard refresh (Ctrl+F5 or Cmd+Shift+R)
3. Check if navbar dropdown is scrollable

## 🎯 One-Line Solution

If you saved the script:
```bash
./production-css-fix.sh
```

This will:
- Auto-detect your web container
- Rebuild CSS
- Collect static files
- Clear CloudFront cache
- Show progress with colors

## ⚡ Emergency Manual Fix

If nothing else works:
```bash
# 1. Rebuild CSS manually
docker exec $(docker ps -q -f name=web) sh -c "cd /app && npm run build-css && python manage.py collectstatic --noinput"

# 2. Force CloudFront refresh via AWS Console
```