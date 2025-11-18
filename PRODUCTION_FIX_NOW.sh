#!/bin/bash
# Quick production fix script

echo "🚀 #FahanieCares Production CSS Fix"
echo "==================================="

# SSH to production and run these commands:
echo "📋 Copy and run these commands on your production server:"
echo ""
echo "cd /path/to/fahanie-cares"
echo "git pull origin main"
echo ""
echo "# Rebuild CSS only (faster option):"
echo "docker exec fahanie-cares-web-1 npm run build-css"
echo "docker exec fahanie-cares-web-1 python manage.py collectstatic --noinput"
echo ""
echo "# OR Full rebuild (slower but thorough):"
echo "docker-compose -f deployment/docker/docker-compose/production.yml build --no-cache web"
echo "docker-compose -f deployment/docker/docker-compose/production.yml up -d"
echo ""
echo "# Then clear CloudFront cache:"
echo "aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths '/*'"
echo ""
echo "==================================="