"""
Middleware for Alpha version feature control
"""
from django.shortcuts import render
from django.conf import settings


class AlphaFeatureMiddleware:
    """
    Middleware to handle access to disabled features during Alpha version
    """
    
    # URL patterns for disabled features
    DISABLED_URL_PATTERNS = [
        'ministries_ppas',
        'ministry_program_detail',
        'category_list',
        'service_list', 
        'service_detail',
        'referral_list',
        'referral_create',
        'referral_detail',
        'referral_update_create',
        'admin_dashboard',
        'program_list',
        'program_create',
        'program_detail',
        'program_update',
        'staff_analytics_dashboard',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if features are disabled in settings
        features = getattr(settings, 'FEATURES', {})
        
        # Get the URL name
        url_name = None
        if hasattr(request, 'resolver_match') and request.resolver_match:
            url_name = request.resolver_match.url_name
        
        # Check if this is a disabled feature
        if url_name in self.DISABLED_URL_PATTERNS:
            # Check if Ministry Programs is disabled
            if (url_name in ['ministries_ppas', 'ministry_program_detail', 'admin_dashboard', 
                           'program_list', 'program_create', 'program_detail', 'program_update'] 
                and not features.get('ministry_programs', True)):
                return render(request, 'core/coming_soon.html', {
                    'feature_name': 'Ministry Programs',
                    'feature_description': 'Explore and manage Bangsamoro Ministry programs and services.',
                    'expected_release': 'Full Release Version'
                })
            
            # Check if Referral System is disabled
            if (url_name in ['category_list', 'service_list', 'service_detail', 'referral_list',
                           'referral_create', 'referral_detail', 'referral_update_create',
                           'staff_analytics_dashboard'] 
                and not features.get('referral_system', True)):
                return render(request, 'core/coming_soon.html', {
                    'feature_name': 'Service Request & Referral System',
                    'feature_description': 'Request services and track referrals through our digital platform.',
                    'expected_release': 'Full Release Version'
                })
        
        response = self.get_response(request)
        return response