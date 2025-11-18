# Systematic Cache Management Solution for #FahanieCares

## Executive Summary
This document provides a comprehensive, long-term solution to prevent CSS and static file caching issues in production. It addresses CloudFront CDN caching, deployment automation, and monitoring.

## 1. Enhanced Static Files Configuration

### 1.1 Update Django Settings

```python
# config/settings/production.py

import hashlib
import os
from datetime import datetime

# Static files versioning
STATIC_VERSION = os.getenv('STATIC_VERSION', hashlib.md5(
    f"{datetime.now().isoformat()}".encode()
).hexdigest()[:8])

# Static files configuration with versioning
STATIC_URL = f'/static/v{STATIC_VERSION}/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise with cache busting
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add cache headers
WHITENOISE_MAX_AGE = 31536000  # 1 year for versioned files
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['map', 'gz']

# CloudFront-aware settings
AWS_CLOUDFRONT_DOMAIN = os.getenv('AWS_CLOUDFRONT_DOMAIN')
if AWS_CLOUDFRONT_DOMAIN:
    STATIC_URL = f'https://{AWS_CLOUDFRONT_DOMAIN}/static/v{STATIC_VERSION}/'
    WHITENOISE_STATIC_PREFIX = f'/static/v{STATIC_VERSION}/'
```

### 1.2 Create Custom Storage Backend

```python
# src/apps/core/storage.py

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.files.storage import Storage
import hashlib

class VersionedStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Adds version hash to static file URLs for aggressive cache busting
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = self._get_version()
    
    def _get_version(self):
        """Generate version from Git commit or timestamp"""
        try:
            import subprocess
            return subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD']
            ).decode('utf-8').strip()
        except:
            return hashlib.md5(
                str(datetime.now()).encode()
            ).hexdigest()[:8]
    
    def url(self, name):
        url = super().url(name)
        if '?' in url:
            url = f"{url}&v={self.version}"
        else:
            url = f"{url}?v={self.version}"
        return url
```

## 2. CloudFront Configuration

### 2.1 Update CloudFront Distribution

```json
{
  "Comment": "#FahanieCares CloudFront Distribution",
  "Origins": [{
    "DomainName": "origin.fahaniecares.ph",
    "Id": "fahaniecares-origin",
    "CustomOriginConfig": {
      "OriginProtocolPolicy": "https-only"
    }
  }],
  "DefaultRootObject": "index.html",
  "CacheBehaviors": [{
    "PathPattern": "/static/*",
    "TargetOriginId": "fahaniecares-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": ["GET", "HEAD"],
    "CachedMethods": ["GET", "HEAD"],
    "Compress": true,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": true,
      "Headers": ["Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"],
      "Cookies": {
        "Forward": "none"
      }
    },
    "ResponseHeadersPolicyId": "cache-control-policy"
  }],
  "CustomErrorResponses": [{
    "ErrorCode": 404,
    "ErrorCachingMinTTL": 300
  }]
}
```

### 2.2 Create Response Headers Policy

```yaml
# cloudfront-headers-policy.yaml
ResponseHeadersPolicy:
  Name: fahaniecares-cache-policy
  CorsConfig:
    AccessControlAllowOrigins:
      Items:
        - "https://fahaniecares.ph"
        - "https://www.fahaniecares.ph"
  CustomHeadersConfig:
    Items:
      - Header: "X-Content-Type-Options"
        Value: "nosniff"
      - Header: "X-Frame-Options"
        Value: "SAMEORIGIN"
  SecurityHeadersConfig:
    StrictTransportSecurity:
      AccessControlMaxAgeSec: 63072000
      IncludeSubdomains: true
      Preload: true
```

## 3. Automated Deployment Pipeline

### 3.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  AWS_REGION: ap-southeast-1
  ECR_REPOSITORY: fahaniecares
  ECS_SERVICE: fahaniecares-service
  ECS_CLUSTER: fahaniecares-cluster

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate Version Hash
        id: version
        run: echo "hash=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Build and Push Docker Image
        env:
          STATIC_VERSION: ${{ steps.version.outputs.hash }}
        run: |
          docker build \
            --build-arg STATIC_VERSION=${STATIC_VERSION} \
            -t $ECR_REPOSITORY:$STATIC_VERSION \
            -f deployment/docker/Dockerfile.production .
          
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker tag $ECR_REPOSITORY:$STATIC_VERSION $ECR_REGISTRY/$ECR_REPOSITORY:$STATIC_VERSION
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$STATIC_VERSION
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment
      
      - name: Invalidate CloudFront Cache
        run: |
          DISTRIBUTION_ID=$(aws cloudfront list-distributions \
            --query "DistributionList.Items[?Aliases.Items[?contains(@, 'fahaniecares.ph')]].Id" \
            --output text)
          
          aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/static/*" "/media/*" "/" "/index.html"
      
      - name: Verify Deployment
        run: |
          sleep 60
          curl -f https://fahaniecares.ph/health/ || exit 1
          
      - name: Notify Deployment Status
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: "Production deployment ${{ job.status }}"
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 3.2 Deployment Script Enhancement

```bash
#!/bin/bash
# deployment/scripts/deploy-with-cache-invalidation.sh

set -e

# Configuration
DEPLOYMENT_ID=$(date +%Y%m%d%H%M%S)
STATIC_VERSION=$(git rev-parse --short HEAD)

echo "🚀 Starting deployment ${DEPLOYMENT_ID}"
echo "📦 Static version: ${STATIC_VERSION}"

# Build with version
docker build \
  --build-arg STATIC_VERSION=${STATIC_VERSION} \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -t fahaniecares:${STATIC_VERSION} \
  -f deployment/docker/Dockerfile.production .

# Tag for registry
docker tag fahaniecares:${STATIC_VERSION} ${ECR_REGISTRY}/fahaniecares:${STATIC_VERSION}
docker tag fahaniecares:${STATIC_VERSION} ${ECR_REGISTRY}/fahaniecares:latest

# Push to registry
docker push ${ECR_REGISTRY}/fahaniecares:${STATIC_VERSION}
docker push ${ECR_REGISTRY}/fahaniecares:latest

# Update service
aws ecs update-service \
  --cluster fahaniecares-cluster \
  --service fahaniecares-service \
  --task-definition fahaniecares:${STATIC_VERSION} \
  --force-new-deployment

# Wait for deployment
echo "⏳ Waiting for deployment to stabilize..."
aws ecs wait services-stable \
  --cluster fahaniecares-cluster \
  --services fahaniecares-service

# Invalidate CloudFront
echo "🔄 Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text)

echo "📝 Invalidation ID: ${INVALIDATION_ID}"

# Wait for invalidation
aws cloudfront wait invalidation-completed \
  --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --id ${INVALIDATION_ID}

echo "✅ Deployment completed successfully!"
```

## 4. CSS Build Process Enhancement

### 4.1 Update Dockerfile for Better Caching

```dockerfile
# deployment/docker/Dockerfile.production

# Build stage with version injection
FROM node:18-alpine AS frontend-builder
ARG STATIC_VERSION
ENV STATIC_VERSION=${STATIC_VERSION}

WORKDIR /app

# Copy package files (cached layer)
COPY src/package*.json ./
RUN npm ci

# Copy source files
COPY src/tailwind.config.js ./
COPY src/static/css/input.css ./static/css/
COPY src/templates ./templates

# Build CSS with version hash
RUN echo "/* Version: ${STATIC_VERSION} */" > static/css/version.css && \
    npm run build-css && \
    cat static/css/version.css static/css/output.css > static/css/output.versioned.css && \
    mv static/css/output.versioned.css static/css/output.css

# Add build metadata
RUN echo "{\"version\": \"${STATIC_VERSION}\", \"buildTime\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > static/build-info.json
```

### 4.2 TailwindCSS Configuration Update

```javascript
// src/tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './apps/**/*.py',  // Include Python files for dynamic classes
  ],
  theme: {
    extend: {
      // Your theme extensions
    },
  },
  plugins: [],
  // Important: Ensure all dynamic classes are included
  safelist: [
    'max-h-[85vh]',
    'max-h-[50vh]',
    'max-h-[60vh]',
    'overflow-y-auto',
    'flex-col',
    'flex-1',
    'min-h-0',
    'flex-shrink-0',
  ]
}
```

## 5. Monitoring and Alerting

### 5.1 Static File Version Endpoint

```python
# src/apps/core/views.py
from django.http import JsonResponse
from django.conf import settings
import os

def static_version_check(request):
    """Health check endpoint that includes static file version"""
    try:
        with open(os.path.join(settings.STATIC_ROOT, 'build-info.json'), 'r') as f:
            build_info = json.load(f)
    except:
        build_info = {"version": "unknown", "buildTime": "unknown"}
    
    return JsonResponse({
        "status": "healthy",
        "staticVersion": getattr(settings, 'STATIC_VERSION', 'unknown'),
        "buildInfo": build_info,
        "cache": {
            "cloudfront": request.META.get('HTTP_X_CACHE', 'unknown'),
            "age": request.META.get('HTTP_AGE', 'unknown')
        }
    })

# src/apps/core/urls.py
urlpatterns = [
    path('health/static-version/', static_version_check, name='static_version_check'),
]
```

### 5.2 CloudWatch Alarms

```yaml
# cloudformation/monitoring.yaml
StaticFileVersionMismatch:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: FahanieCares-StaticVersionMismatch
    MetricName: StaticVersionMismatch
    Namespace: FahanieCares
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SNSAlertTopic
```

### 5.3 Automated Version Check Script

```python
#!/usr/bin/env python3
# scripts/check_static_version.py

import requests
import boto3
import json
from datetime import datetime

def check_static_versions():
    """Compare static versions across origin and CDN"""
    
    # Check origin
    origin_response = requests.get('https://origin.fahaniecares.ph/health/static-version/')
    origin_data = origin_response.json()
    
    # Check CDN
    cdn_response = requests.get('https://fahaniecares.ph/health/static-version/')
    cdn_data = cdn_response.json()
    
    # Compare versions
    if origin_data['staticVersion'] != cdn_data['staticVersion']:
        # Send alert
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.put_metric_data(
            Namespace='FahanieCares',
            MetricData=[{
                'MetricName': 'StaticVersionMismatch',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [{
                    'Name': 'Environment',
                    'Value': 'production'
                }]
            }]
        )
        
        print(f"⚠️  Version mismatch detected!")
        print(f"Origin: {origin_data['staticVersion']}")
        print(f"CDN: {cdn_data['staticVersion']}")
        return False
    
    print(f"✅ Versions match: {origin_data['staticVersion']}")
    return True

if __name__ == '__main__':
    check_static_versions()
```

## 6. Development Workflow Integration

### 6.1 Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check if CSS changes are included
if git diff --cached --name-only | grep -q "\.css$\|tailwind\.config\.js\|\.html$"; then
    echo "🎨 CSS changes detected, rebuilding..."
    cd src && npm run build-css
    git add static/css/output.css
fi
```

### 6.2 Local Development Script

```bash
#!/bin/bash
# scripts/dev-with-cache-preview.sh

# Simulate production cache behavior locally
export STATIC_VERSION=$(git rev-parse --short HEAD)

# Start Django with cache headers
python manage.py runserver --settings=config.settings.development \
  --insecure \
  --nostatic &

# Start static file server with cache headers
python -m http.server 8001 \
  --directory staticfiles \
  --bind 127.0.0.1 &

echo "🚀 Development server running with cache simulation"
echo "📦 Static version: ${STATIC_VERSION}"
echo "🌐 Access at: http://localhost:8000"
```

## 7. Documentation and Training

### 7.1 Deployment Checklist

```markdown
# Deployment Checklist

Before deploying:
- [ ] Run `npm run build-css` locally
- [ ] Verify CSS changes in browser
- [ ] Check `git status` includes output.css
- [ ] Run tests: `python manage.py test`

During deployment:
- [ ] Monitor deployment logs
- [ ] Check CloudFront invalidation status
- [ ] Verify static version endpoint

After deployment:
- [ ] Clear browser cache and test
- [ ] Check static version matches
- [ ] Monitor error rates
- [ ] Verify CSS changes are live
```

### 7.2 Troubleshooting Guide

```markdown
# CSS Not Updating - Troubleshooting

1. Check static version:
   ```bash
   curl https://fahaniecares.ph/health/static-version/
   ```

2. Force CloudFront invalidation:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id E1234567890ABC \
     --paths "/*"
   ```

3. Check CSS directly:
   ```bash
   curl -I https://fahaniecares.ph/static/css/output.css
   # Look for: x-cache: Miss from cloudfront (good)
   # Or: x-cache: Hit from cloudfront (cached)
   ```

4. Bypass cache for testing:
   ```
   https://fahaniecares.ph/static/css/output.css?nocache=timestamp
   ```
```

## 8. Implementation Timeline

### Phase 1: Immediate (Week 1)
- Implement CloudFront invalidation in deployment script
- Add static version endpoint
- Update deployment documentation

### Phase 2: Short-term (Week 2-3)
- Implement GitHub Actions workflow
- Add monitoring and alerts
- Train team on new process

### Phase 3: Long-term (Month 2)
- Implement custom storage backend
- Add automated testing for CSS builds
- Create dashboard for deployment status

## 9. Success Metrics

- **Cache Hit Rate**: Monitor CloudFront metrics
- **Deployment Time**: Track time from commit to live
- **Version Mismatch Incidents**: Should be zero
- **User Reports**: CSS update issues should drop to zero

## 10. Conclusion

This systematic approach ensures:
1. **Automatic cache invalidation** on every deployment
2. **Version tracking** for debugging
3. **Monitoring** to catch issues early
4. **Clear workflows** to prevent human error
5. **Fast rollback** capabilities

The key is automation - removing manual steps that can be forgotten or done incorrectly.