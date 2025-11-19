#!/bin/bash
# Emergency CSS cache fix script for #FahanieCares
# Run this to immediately clear CloudFront cache

echo "🚨 #FahanieCares CSS Cache Fix"
echo "=============================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    echo "Please install it first: https://aws.amazon.com/cli/"
    exit 1
fi

# Try to find CloudFront distribution
echo "🔍 Looking for CloudFront distribution..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Aliases.Items[?contains(@, 'fahaniecares.ph')]].Id" \
    --output text 2>/dev/null)

if [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ Could not find CloudFront distribution automatically"
    echo ""
    echo "Please enter your CloudFront Distribution ID:"
    echo "(You can find this in AWS Console > CloudFront)"
    read -p "Distribution ID: " DISTRIBUTION_ID
fi

if [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ No distribution ID provided"
    exit 1
fi

echo "📦 Distribution ID: $DISTRIBUTION_ID"

# Create invalidation
echo "🔄 Creating cache invalidation..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Invalidation created successfully!"
    echo "📝 Invalidation ID: $INVALIDATION_ID"
    echo ""
    echo "⏳ Waiting for invalidation to complete (this may take 5-10 minutes)..."
    
    # Wait for invalidation
    aws cloudfront wait invalidation-completed \
        --distribution-id $DISTRIBUTION_ID \
        --id $INVALIDATION_ID 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Cache invalidation completed!"
    else
        echo "⚠️  Invalidation is in progress but wait timed out"
        echo "   It will complete in the background"
    fi
else
    echo "❌ Failed to create invalidation"
    echo "Error: $INVALIDATION_ID"
    echo ""
    echo "Possible issues:"
    echo "1. Check your AWS credentials are configured"
    echo "2. Ensure you have CloudFront permissions"
    echo "3. Verify the distribution ID is correct"
    exit 1
fi

echo ""
echo "🎉 Done! Your CSS updates should now be visible."
echo ""
echo "📌 Next steps:"
echo "1. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)"
echo "2. Check https://fahaniecares.ph"
echo "3. If still not working, wait 5 more minutes and try again"
echo ""
echo "💡 To automate this in the future:"
echo "   Add this to your deployment script:"
echo "   aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths '/*'"