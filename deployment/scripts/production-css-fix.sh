#!/bin/bash
# Production CSS Quick Fix Script for #FahanieCares
# This script rebuilds CSS and clears CloudFront cache without full Docker rebuild

set -e

echo "🚀 #FahanieCares Production CSS Quick Fix"
echo "========================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Find the web container
echo -e "${YELLOW}Step 1: Finding web container...${NC}"
WEB_CONTAINER=$(docker ps --format "table {{.Names}}" | grep -E "(web|django)" | head -1)

if [ -z "$WEB_CONTAINER" ]; then
    echo -e "${RED}❌ Could not find web container automatically${NC}"
    echo "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    echo ""
    read -p "Please enter the web container name: " WEB_CONTAINER
fi

echo -e "${GREEN}✅ Using container: $WEB_CONTAINER${NC}"
echo ""

# Step 2: Rebuild CSS inside container
echo -e "${YELLOW}Step 2: Rebuilding CSS with TailwindCSS...${NC}"
docker exec $WEB_CONTAINER npm run build-css

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ CSS rebuilt successfully${NC}"
else
    echo -e "${RED}❌ CSS rebuild failed${NC}"
    exit 1
fi
echo ""

# Step 3: Collect static files
echo -e "${YELLOW}Step 3: Collecting static files...${NC}"
docker exec $WEB_CONTAINER python manage.py collectstatic --noinput

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Static files collected${NC}"
else
    echo -e "${RED}❌ Static file collection failed${NC}"
    exit 1
fi
echo ""

# Step 4: Clear CloudFront cache
echo -e "${YELLOW}Step 4: Clearing CloudFront cache...${NC}"

# Try to get distribution ID from environment or find it
if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo "Searching for CloudFront distribution..."
    CLOUDFRONT_DISTRIBUTION_ID=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?contains(Aliases.Items || [''], 'fahaniecares.ph')].Id" \
        --output text 2>/dev/null)
fi

if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "${RED}❌ Could not find CloudFront distribution ID${NC}"
    echo ""
    echo "Please enter your CloudFront Distribution ID:"
    echo "(You can find this in AWS Console > CloudFront)"
    read -p "Distribution ID: " CLOUDFRONT_DISTRIBUTION_ID
fi

if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo "Creating invalidation for distribution: $CLOUDFRONT_DISTRIBUTION_ID"
    
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text 2>&1)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ CloudFront invalidation created: $INVALIDATION_ID${NC}"
        echo ""
        echo "⏳ Waiting for cache to clear (this may take 5-10 minutes)..."
        
        # Optional: Wait for completion
        aws cloudfront wait invalidation-completed \
            --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
            --id $INVALIDATION_ID 2>/dev/null || true
            
        echo -e "${GREEN}✅ Cache invalidation completed!${NC}"
    else
        echo -e "${RED}❌ CloudFront invalidation failed${NC}"
        echo "Error: $INVALIDATION_ID"
        echo ""
        echo "You can manually invalidate in AWS Console:"
        echo "1. Go to CloudFront"
        echo "2. Select your distribution"
        echo "3. Create invalidation with path: /*"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping CloudFront invalidation (no distribution ID)${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}🎉 CSS Fix Complete!${NC}"
echo ""
echo "📌 Verification steps:"
echo "1. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)"
echo "2. Check https://fahaniecares.ph"
echo "3. The navbar dropdown should now be scrollable"
echo ""
echo "💡 If still not working:"
echo "- Wait 5 more minutes for CloudFront"
echo "- Try incognito/private browsing mode"
echo "- Check browser console for CSS errors"