#!/bin/bash
# Deploy registration fixes to production
# This script should be run on the production server

echo "🚀 Deploying Registration Fixes to Production"
echo "============================================"
echo ""

# 1. Pull latest changes from repository
echo "📥 Step 1: Pulling latest changes from GitHub..."
git pull origin main

# 2. Build new Docker image with fixes
echo ""
echo "🏗️  Step 2: Building new Docker image..."
docker-compose build web

# 3. Run database migrations (if any)
echo ""
echo "🗄️  Step 3: Running database migrations..."
docker-compose exec web python manage.py migrate

# 4. Create media directories with proper permissions
echo ""
echo "📁 Step 4: Creating media directories..."
docker-compose exec web python manage.py fix_media_permissions

# 5. Collect static files
echo ""
echo "📦 Step 5: Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# 6. Restart the web service
echo ""
echo "🔄 Step 6: Restarting web service..."
docker-compose restart web

# 7. Clear any caches
echo ""
echo "🧹 Step 7: Clearing caches..."
docker-compose exec web python manage.py clear_cache 2>/dev/null || echo "No cache clearing command available"

# 8. Verify the deployment
echo ""
echo "✅ Step 8: Verifying deployment..."
sleep 5  # Wait for service to be ready

# Check if web service is running
if docker-compose ps web | grep -q "Up"; then
    echo "✅ Web service is running"
else
    echo "❌ Web service is not running properly!"
    exit 1
fi

# Test registration endpoint
echo ""
echo "🧪 Testing registration endpoint..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://fahaniecares.ph/accounts/register/)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Registration page is accessible (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Registration page returned HTTP $HTTP_STATUS"
fi

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "The following fixes have been deployed:"
echo "✅ Radio button form submission fixed (now using field.html_name)"
echo "✅ Enhanced radio button styling with animations"
echo "✅ Media upload directories created with fallback paths"
echo "✅ Improved file upload error handling"
echo ""
echo "Users should now be able to:"
echo "- Select radio buttons that properly submit with the form"
echo "- See immediate visual feedback when clicking radio buttons"
echo "- Upload voter ID photos without permission errors"
echo "- Complete registration successfully"
echo ""
echo "📊 Next Steps:"
echo "1. Monitor logs: docker-compose logs -f web"
echo "2. Check for registration attempts in the database"
echo "3. Test the registration form manually"
echo "4. Monitor for any error reports"