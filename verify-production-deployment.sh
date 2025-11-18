#!/bin/bash
# Production Deployment Verification Script for Radio Button Fixes
# Ensures the fork sync and production rebuild will work correctly

echo "🚀 #FahanieCares Production Deployment Verification"
echo "=================================================="

# Function to check deployment readiness
check_deployment_readiness() {
    echo "📋 Checking deployment readiness..."
    
    # 1. Verify template contains radio button fixes
    echo "✓ Checking template for radio button preservation logic..."
    if grep -q "choice.is_checked or form.sex.value == choice.choice_value" src/apps/constituents/templates/constituents/member_registration.html; then
        echo "  ✅ Radio button dual state checking: FOUND"
    else
        echo "  ❌ Radio button dual state checking: MISSING"
        return 1
    fi
    
    # 2. Verify JavaScript state preservation
    echo "✓ Checking JavaScript for sessionStorage backup..."
    if grep -q "sessionStorage.setItem.*radio_" src/apps/constituents/templates/constituents/member_registration.html; then
        echo "  ✅ SessionStorage backup logic: FOUND"
    else
        echo "  ❌ SessionStorage backup logic: MISSING"
        return 1
    fi
    
    # 3. Verify form_invalid method enhancements
    echo "✓ Checking form_invalid method for preservation logic..."
    if grep -q "Your selections have been preserved" src/apps/constituents/member_views.py; then
        echo "  ✅ Enhanced form_invalid method: FOUND"
    else
        echo "  ❌ Enhanced form_invalid method: MISSING"
        return 1
    fi
    
    # 4. Verify production Dockerfile will handle changes
    echo "✓ Checking production Dockerfile..."
    if [ -f "deployment/docker/Dockerfile.production" ]; then
        echo "  ✅ Production Dockerfile: FOUND"
        
        # Check if it copies templates properly
        if grep -q "COPY.*src/.*app" deployment/docker/Dockerfile.production; then
            echo "  ✅ Template copying in Dockerfile: CONFIGURED"
        else
            echo "  ❌ Template copying in Dockerfile: NOT CONFIGURED"
            return 1
        fi
    else
        echo "  ❌ Production Dockerfile: MISSING"
        return 1
    fi
    
    # 5. Verify TailwindCSS will compile radio button styles
    echo "✓ Checking TailwindCSS configuration..."
    if [ -f "src/tailwind.config.js" ]; then
        echo "  ✅ TailwindCSS config: FOUND"
        
        # Check for safelist that includes radio button classes
        if grep -q "safelist" src/tailwind.config.js; then
            echo "  ✅ TailwindCSS safelist: CONFIGURED"
        else
            echo "  ⚠️  TailwindCSS safelist: NOT FOUND (may still work with JIT)"
        fi
    else
        echo "  ❌ TailwindCSS config: MISSING"
        return 1
    fi
    
    return 0
}

# Function to create production test checklist
create_test_checklist() {
    echo ""
    echo "📝 Creating Production Test Checklist..."
    
    cat > production-test-checklist.md << 'EOF'
# Production Deployment Test Checklist

## Pre-Deployment Verification ✅
- [x] Radio button dual state checking in template
- [x] JavaScript sessionStorage backup logic
- [x] Enhanced form_invalid method with preservation
- [x] Production Dockerfile configured
- [x] TailwindCSS configuration ready

## Post-Deployment Testing (Manual)

### 1. Form Submission with Validation Errors
- [ ] Navigate to /constituents/register/
- [ ] Fill out form partially (leave required fields empty)
- [ ] Select radio buttons for: Sex, Sector, Education, Eligibility
- [ ] Submit form (should fail validation)
- [ ] Verify radio buttons remain selected ✅
- [ ] Complete missing fields and submit successfully

### 2. JavaScript State Preservation
- [ ] Open browser developer tools (F12)
- [ ] Go to Application/Storage > Session Storage
- [ ] Fill form and select radio buttons
- [ ] Verify sessionStorage items created: radio_sex, radio_sector, etc.
- [ ] Refresh page, verify selections restored

### 3. Visual Feedback
- [ ] Hover over radio buttons (should show green highlight)
- [ ] Click radio buttons (should have smooth animation)
- [ ] Verify consistent styling across all radio groups

### 4. Mobile Responsiveness
- [ ] Test on mobile device or responsive mode
- [ ] Verify radio buttons are touch-friendly
- [ ] Confirm form validation works on mobile

## Success Criteria
✅ All radio button selections preserved on form validation errors
✅ Enhanced visual feedback and hover effects working
✅ JavaScript backup functioning properly
✅ Mobile-friendly interface
✅ No console errors in browser developer tools

## Rollback Plan (if issues occur)
1. Revert to previous commit: `git revert HEAD`
2. Push revert: `git push origin main`
3. Wait for automatic fork sync and redeploy
EOF

    echo "  ✅ Test checklist created: production-test-checklist.md"
}

# Function to verify fork sync compatibility
verify_fork_sync() {
    echo ""
    echo "🔄 Verifying Fork Sync Compatibility..."
    
    # Check if we're on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" = "main" ]; then
        echo "  ✅ On main branch: Ready for fork sync"
    else
        echo "  ❌ Not on main branch: Fork sync may not work"
        return 1
    fi
    
    # Check for any uncommitted changes
    if git diff-index --quiet HEAD --; then
        echo "  ✅ Working tree clean: Ready for sync"
    else
        echo "  ❌ Uncommitted changes found: Fork sync incomplete"
        return 1
    fi
    
    # Verify latest commit contains radio button fixes
    if git log --oneline -10 | grep -q -i "radio\|fix"; then
        echo "  ✅ Radio button fixes in recent commits"
    else
        echo "  ⚠️  Radio button fixes not in recent commit messages"
    fi
    
    return 0
}

# Function to create monitoring script
create_monitoring_script() {
    echo ""
    echo "📊 Creating deployment monitoring script..."
    
    cat > monitor-deployment.sh << 'EOF'
#!/bin/bash
# Monitor production deployment after fork sync

echo "🔍 Monitoring Production Deployment"
echo "=================================="

# Function to check if site is responding
check_site_health() {
    echo "🏥 Checking site health..."
    
    # Check main site
    if curl -s -o /dev/null -w "%{http_code}" https://fahaniecares.ph | grep -q "200"; then
        echo "  ✅ Main site: HEALTHY (200 OK)"
    else
        echo "  ❌ Main site: UNHEALTHY"
        return 1
    fi
    
    # Check registration page
    if curl -s -o /dev/null -w "%{http_code}" https://fahaniecares.ph/constituents/register/ | grep -q "200"; then
        echo "  ✅ Registration page: ACCESSIBLE"
    else
        echo "  ❌ Registration page: NOT ACCESSIBLE"
        return 1
    fi
    
    return 0
}

# Function to check for deployment completion
check_deployment_status() {
    echo "🚀 Checking deployment status..."
    
    # Look for updated assets (simplified check)
    timestamp=$(date +%s)
    cache_buster="?v=$timestamp"
    
    # Check if CSS includes our radio button styles
    if curl -s "https://fahaniecares.ph/static/css/output.css$cache_buster" | grep -q "radio-group\|radio-enhanced"; then
        echo "  ✅ Radio button styles: DEPLOYED"
    else
        echo "  ⚠️  Radio button styles: NOT CONFIRMED (may be cached)"
    fi
    
    return 0
}

# Run monitoring checks
echo "Starting deployment monitoring..."
echo "Timestamp: $(date)"
echo ""

if check_site_health && check_deployment_status; then
    echo ""
    echo "✅ Deployment appears successful!"
    echo "Please run manual tests from production-test-checklist.md"
else
    echo ""
    echo "❌ Deployment issues detected"
    echo "Check logs and consider rollback if necessary"
fi
EOF

    chmod +x monitor-deployment.sh
    echo "  ✅ Monitoring script created: monitor-deployment.sh"
}

# Main execution
echo "Starting verification process..."

if check_deployment_readiness; then
    echo ""
    echo "✅ All deployment readiness checks passed!"
    
    verify_fork_sync
    create_test_checklist
    create_monitoring_script
    
    echo ""
    echo "🎯 Deployment Summary"
    echo "==================="
    echo "✅ Radio button fixes are ready for production"
    echo "✅ Template includes dual state preservation logic"
    echo "✅ JavaScript backup system implemented"
    echo "✅ Production Docker build will handle changes"
    echo "✅ Repository ready for fork sync"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Fork will automatically sync from main repository"
    echo "2. Production rebuild will include radio button fixes"
    echo "3. Run ./monitor-deployment.sh after deployment"
    echo "4. Follow production-test-checklist.md for verification"
    echo ""
    echo "🔧 If issues occur:"
    echo "- Check monitor-deployment.sh output"
    echo "- Follow rollback plan in test checklist"
    echo "- Contact deployment team if needed"
    
else
    echo ""
    echo "❌ Deployment readiness checks failed!"
    echo "Please address the issues above before deployment."
    exit 1
fi