import os

# Determine which settings file to load based on DJANGO_SETTINGS_MODULE environment variable
# Default to development settings if DJANGO_SETTINGS_MODULE is not explicitly set
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Extract the last part of the module name (e.g., 'development' or 'production')
# and import it dynamically.
if settings_module.endswith('.production'):
    from .production import *
elif settings_module.endswith('.development'):
    from .development import *
else:
    # Fallback to base settings if no specific environment is matched
    from .base import *

# Ensure BASE_DIR is available from the imported settings
if 'BASE_DIR' not in locals():
    from .base import BASE_DIR
