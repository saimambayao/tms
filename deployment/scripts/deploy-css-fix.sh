#!/bin/bash
# One-command production CSS fix for #FahanieCares
# Just run: curl -s https://raw.githubusercontent.com/tech-bangsamoro/fahanie-cares/main/deploy-css-fix.sh | bash

set -e

echo "🚀 #FahanieCares Automated CSS Fix"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Pull latest changes
echo -e "${YELLOW}📥 Pulling latest changes from Git...${NC}"
git pull origin main || {
    echo -e "${RED}❌ Git pull failed. Continuing anyway...${NC}"
}

# Step 2: Find web container automatically
echo -e "${YELLOW}🔍 Finding web container...${NC}"
WEB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(web|django|fahanie)" | head -1)

if [ -z "$WEB_CONTAINER" ]; then
    # Try alternative search
    WEB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -v "db\|redis\|nginx" | head -1)
fi

if [ -z "$WEB_CONTAINER" ]; then
    echo -e "${RED}❌ Could not find web container${NC}"
    docker ps --format "table {{.Names}}\t{{.Image}}"
    exit 1
fi

echo -e "${GREEN}✅ Found container: $WEB_CONTAINER${NC}"

# Step 3: Rebuild CSS
echo -e "${YELLOW}🎨 Rebuilding CSS...${NC}"
docker exec $WEB_CONTAINER sh -c "cd /app && npm run build-css" || {
    # Fallback: try without cd
    docker exec $WEB_CONTAINER npm run build-css || {
        echo -e "${RED}❌ CSS rebuild failed${NC}"
        exit 1
    }
}
echo -e "${GREEN}✅ CSS rebuilt${NC}"

# Step 4: Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
docker exec $WEB_CONTAINER python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Static files collected${NC}"

# Step 5: Clear CloudFront cache (if AWS CLI available)
echo -e "${YELLOW}🔄 Clearing CloudFront cache...${NC}"

if command -v aws &> /dev/null; then
    # Try to find distribution automatically
    DIST_ID=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?contains(Aliases.Items || [''], 'fahaniecares.ph')].Id" \
        --output text 2>/dev/null)
    
    if [ ! -z "$DIST_ID" ]; then
        echo "Found distribution: $DIST_ID"
        INVALIDATION_ID=$(aws cloudfront create-invalidation \
            --distribution-id $DIST_ID \
            --paths "/*" \
            --query 'Invalidation.Id' \
            --output text 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ CloudFront cache cleared: $INVALIDATION_ID${NC}"
        else
            echo -e "${YELLOW}⚠️  CloudFront invalidation failed - clear manually${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not find CloudFront distribution${NC}"
        echo "Clear cache manually in AWS Console"
    fi
else
    echo -e "${YELLOW}⚠️  AWS CLI not found - clear cache manually:${NC}"
    echo "1. Go to AWS Console > CloudFront"
    echo "2. Select your distribution"
    echo "3. Create invalidation with path: /*"
fi

# Done!
echo ""
echo -e "${GREEN}=================================="
echo "🎉 CSS Fix Complete!"
echo "==================================${NC}"
echo ""
echo "Next steps:"
echo "1. Wait 2-5 minutes for CloudFront"
echo "2. Visit https://fahaniecares.ph"
echo "3. Hard refresh (Ctrl+F5)"
echo ""
echo -e "${BLUE}The navbar dropdown should now be scrollable!${NC}"