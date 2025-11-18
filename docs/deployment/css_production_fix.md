# CSS Production Update Fix

## Issue
The navbar dropdown scroll fix works locally but not on fahaniecares.ph because CloudFront is caching the old CSS file.

## Root Cause
1. **CloudFront CDN Caching**: Production uses CloudFront CDN which caches static files including CSS
2. **CSS Build Process**: The new TailwindCSS classes (`max-h-[85vh]`, `flex-col`, etc.) need to be compiled and deployed

## Solution Steps

### 1. Immediate Fix - CloudFront Cache Invalidation

If you have AWS access, invalidate the CloudFront cache:
```bash
# Invalidate all CSS files
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/static/css/*" "/css/*"
```

### 2. Force Browser Cache Refresh
Users can force refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

### 3. Deployment Fix - Ensure CSS is Rebuilt

The production Dockerfile already includes CSS build (Stage 1), but ensure it runs:

```bash
# Force rebuild without cache
docker build --no-cache -t fahaniecares:latest -f deployment/docker/Dockerfile.production .

# Or if using the deployment script
./deployment/scripts/deploy.sh
```

### 4. Verify CSS Content

Check if the new classes are in the production CSS:
```bash
# SSH into production and check
curl https://fahaniecares.ph/static/css/output.css | grep "max-h-\\\[85vh\\\]"
```

### 5. Alternative Quick Fix - Inline Styles

If cache invalidation is not possible immediately, add inline styles temporarily:
```html
<!-- In modern_navbar.html, add style attribute -->
<div ... style="max-height: 85vh; overflow-y: auto;">
```

### 6. Long-term Solution - Cache Busting

Add version hash to CSS files in production:
```python
# In settings/production.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

This will append hash to filenames (e.g., `output.abc123.css`) forcing cache updates.

## Verification Steps

1. Check if CSS is updated: View page source and look for the CSS file URL
2. Inspect the dropdown element to see if new classes are applied
3. Check browser console for any CSS loading errors

## AWS CloudFront Distribution ID

To find your distribution ID:
```bash
aws cloudfront list-distributions --query "DistributionList.Items[?Contains(Aliases.Items, 'fahaniecares.ph')].Id" --output text
```

## Contact DevOps

If you don't have AWS access, contact your DevOps team to:
1. Invalidate CloudFront cache for `/static/css/*`
2. Ensure the latest Docker image is deployed
3. Verify the CSS build step completed successfully in deployment logs