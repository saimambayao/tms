"""
URL configuration for #FahanieCares project.
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # Import i18n_patterns

# Customize admin site
admin.site.site_header = "#FahanieCares Administration"
admin.site.site_title = "#FahanieCares Admin"
admin.site.index_title = "Welcome to #FahanieCares Admin Panel"

# Main URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('services/', include('apps.services.urls')),  # Temporarily moved outside i18n_patterns for testing
    path('i18n/', include('django.conf.urls.i18n')), # Add the set_language view
]

# URL patterns wrapped with i18n_patterns
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.users.urls')),
    path('', include('apps.referrals.urls')),
    path('staff/', include('apps.staff.urls')),
    path('', include('apps.constituents.urls')),
    path('chapters/', include('apps.chapters.urls')),
    path('documents/', include('apps.documents.urls')),
    path('notifications/', include('apps.notifications.urls')),
    # path('search/', include('apps.search.urls')),
    path('dashboards/', include('apps.dashboards.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('cooperatives/', include('apps.cooperatives.urls')),
    path('unified-db/', include('apps.unified_db.urls')),
    # Add other app URLs as they're created
)

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
