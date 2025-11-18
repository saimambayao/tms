from django.urls import path
from . import views, api_views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/summary-data/', api_views.summary_data, name='api_summary_data'),
    path('api/gender-distribution/', api_views.gender_distribution, name='api_gender_distribution'),
    path('api/age-distribution/', api_views.age_distribution, name='api_age_distribution'),
    path('api/membership-status-distribution/', api_views.membership_status_distribution, name='api_membership_status_distribution'),
    path('api/sector-distribution/', api_views.sector_distribution, name='api_sector_distribution'),
    path('api/registration-trend/', api_views.registration_trend, name='api_registration_trend'),
    path('api/sector-status-distribution/', api_views.sector_status_distribution, name='api_sector_status_distribution'),
]
