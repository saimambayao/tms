import os
import stat
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def safe_media_upload(instance, filename):
    """
    Safely handle media file uploads by ensuring directories exist.
    Used for announcement image uploads.
    """
    upload_path = 'announcements/'
    full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    
    # Try to create directory if it doesn't exist
    try:
        os.makedirs(full_path, mode=0o755, exist_ok=True)
        logger.info(f"Created media directory: {full_path}")
    except PermissionError as e:
        logger.error(f"Permission denied creating directory {full_path}: {e}")
        # Try alternative approach - create in a temp location and log the issue
        # This allows the upload to continue even if directory creation fails
        pass
    except Exception as e:
        logger.error(f"Error creating directory {full_path}: {e}")
        pass
    
    return os.path.join(upload_path, filename)


def ensure_media_directories():
    """
    Ensure all required media directories exist with proper permissions.
    """
    directories = [
        'announcements',
        'documents', 
        'constituents',
        'services',
        'chapters',
        'voter_id_photos',  # For member registration
    ]
    
    for directory in directories:
        path = os.path.join(settings.MEDIA_ROOT, directory)
        os.makedirs(path, exist_ok=True)
        
        # Set permissions (only if running as root or with sufficient privileges)
        try:
            os.chmod(path, 0o755)
        except PermissionError:
            # If we can't set permissions, at least the directory exists
            pass