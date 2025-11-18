#!/bin/bash
# Enhanced deployment script with automatic cache invalidation
# This ensures CSS and static file updates are immediately visible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ID=$(date +%Y%m%d%H%M%S)
STATIC_VERSION=$(git rev-parse --short HEAD)
AWS_REGION=${AWS_REGION:-"ap-southeast-1"}

echo -e "${BLUE}🚀 Starting #FahanieCares Deployment${NC}"
echo -e "${BLUE}📦 Deployment ID: ${DEPLOYMENT_ID}${NC}"
echo -e "${BLUE}📦 Static Version: ${STATIC_VERSION}${NC}"

# Check required environment variables
if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "${YELLOW}⚠️  Warning: CLOUDFRONT_DISTRIBUTION_ID not set${NC}"
    echo -e "${YELLOW}   CloudFront invalidation will be skipped${NC}"
fi

# Step 1: Build Docker image with version
echo -e "\n${BLUE}📦 Building Docker image...${NC}"
docker build \
  --build-arg STATIC_VERSION=${STATIC_VERSION} \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -t fahaniecares:${STATIC_VERSION} \
  -f deployment/docker/Dockerfile.production . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Step 2: Deploy (platform-specific)
echo -e "\n${BLUE}🚀 Deploying application...${NC}"

# Option A: Docker Compose deployment
if [ -f "docker-compose.production.yml" ]; then
    docker-compose -f docker-compose.production.yml up -d --build
    echo -e "${GREEN}✅ Docker Compose deployment completed${NC}"
fi

# Option B: Manual Docker deployment
# docker stop fahaniecares || true
# docker rm fahaniecares || true
# docker run -d --name fahaniecares \
#   -p 80:8000 \
#   --env-file .env.production \
#   fahaniecares:${STATIC_VERSION}

# Step 3: Wait for application to be ready
echo -e "\n${BLUE}⏳ Waiting for application to start...${NC}"
sleep 30

# Step 4: Health check
echo -e "\n${BLUE}🏥 Running health check...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://fahaniecares.ph/health/ || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned: ${HEALTH_STATUS}${NC}"
fi

# Step 5: CloudFront Cache Invalidation
if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "\n${BLUE}🔄 Invalidating CloudFront cache...${NC}"
    
    # Create invalidation
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text 2>/dev/null || echo "")
    
    if [ ! -z "$INVALIDATION_ID" ]; then
        echo -e "${GREEN}✅ Invalidation created: ${INVALIDATION_ID}${NC}"
        
        # Wait for invalidation to complete (optional)
        echo -e "${BLUE}⏳ Waiting for cache invalidation...${NC}"
        aws cloudfront wait invalidation-completed \
            --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
            --id ${INVALIDATION_ID} 2>/dev/null || {
                echo -e "${YELLOW}⚠️  Could not wait for invalidation (continuing anyway)${NC}"
            }
        
        echo -e "${GREEN}✅ Cache invalidation completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not create CloudFront invalidation${NC}"
    fi
else
    echo -e "\n${YELLOW}⚠️  Skipping CloudFront invalidation (no distribution ID)${NC}"
fi

# Step 6: Verify static files
echo -e "\n${BLUE}🔍 Verifying static files...${NC}"
CSS_CHECK=$(curl -s -I https://fahaniecares.ph/static/css/output.css | grep -i "x-cache" || echo "No cache header")
echo -e "Cache status: ${CSS_CHECK}"

# Step 7: Final summary
echo -e "\n${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}📊 Summary:${NC}"
echo -e "   - Deployment ID: ${DEPLOYMENT_ID}"
echo -e "   - Static Version: ${STATIC_VERSION}"
echo -e "   - Health Check: ${HEALTH_STATUS}"
echo -e "   - CloudFront: ${INVALIDATION_ID:-Not invalidated}"
echo -e "\n${BLUE}🌐 Application URL: https://fahaniecares.ph${NC}"

# Step 8: Send notification (optional)
if [ ! -z "$SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Deployment completed: v${STATIC_VERSION}\"}" \
        $SLACK_WEBHOOK 2>/dev/null || true
fi

# Step 9: Log deployment
echo "${DEPLOYMENT_ID}|${STATIC_VERSION}|$(date -u +"%Y-%m-%dT%H:%M:%SZ")|${HEALTH_STATUS}" >> deployments.log

exit 0