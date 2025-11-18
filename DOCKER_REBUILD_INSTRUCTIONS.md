# Docker Rebuild Instructions for CSS Fix

## Quick Answer: YES, you need to rebuild

The CSS classes (`max-h-[85vh]`, `flex-col`, etc.) need to be compiled by TailwindCSS.

## For Local Development

Since you use volume mounts, just rebuild CSS:
```bash
docker-compose exec web npm run build-css
```

## For Production Deployment

### Option 1: Full Rebuild (Recommended)
```bash
# Commit all changes first
git add -A
git commit -m "Fix navbar dropdown scroll issue with height limits"
git push origin main

# Then on production server:
docker-compose -f docker-compose.production.yml build --no-cache web
docker-compose -f docker-compose.production.yml up -d

# Clear CloudFront cache
./fix-css-cache-now.sh
```

### Option 2: Quick CSS Update Only
```bash
# SSH to production server
docker-compose -f docker-compose.production.yml exec web npm run build-css
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Clear CloudFront cache
./fix-css-cache-now.sh
```

## What Changed That Requires Rebuild

1. **HTML Templates**: Added new TailwindCSS classes
   - `max-h-[85vh]` - Limits dropdown height
   - `flex flex-col` - Flexbox layout
   - `overflow-y-auto` - Scrollable content
   - `flex-shrink-0` - Fixed footer

2. **TailwindCSS Config**: Added safelist to ensure classes are always included

3. **Deployment Scripts**: Enhanced with automatic cache invalidation

## Verification Steps

After rebuild and deployment:
```bash
# Check if new CSS is included
curl https://fahaniecares.ph/static/css/output.css | grep "max-h-\\\[85vh\\\]"

# Should return CSS rules for the new classes
```

## Timeline

1. **Now**: Run local CSS rebuild to test
2. **Commit**: Push changes to Git
3. **Deploy**: Rebuild production Docker image
4. **Cache**: Clear CloudFront cache
5. **Verify**: Test dropdown on production site

Total time: ~10-15 minutes