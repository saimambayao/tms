#!/bin/bash
# Deploy radio button fix to production

echo "🔘 Deploying Radio Button Fix to Production"
echo "========================================"

# Pull latest changes on production
echo "📥 Pulling latest changes..."
git pull origin main

# Restart web service to pick up template changes
echo "🔄 Restarting web service..."
docker-compose restart web || docker-compose restart fahanie-cares-web-1

echo ""
echo "✅ Radio button fix deployed!"
echo ""
echo "The fix includes:"
echo "- Radio buttons now preserve state on form errors"
echo "- Enhanced visual feedback and hover effects"
echo "- JavaScript backup for state preservation"
echo ""
echo "Users will no longer lose their radio button selections"
echo "when the registration form has validation errors."