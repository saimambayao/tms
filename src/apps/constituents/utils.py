import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

MUNICIPALITY_CHOICES_DATA = {
    'Maguindanao del Sur': [
        'Ampatuan', 'Buluan', 'Datu Abdullah Sangki', 'Datu Anggal Midtimbang',
        'Datu Hoffer Ampatuan', 'Datu Paglas', 'Datu Piang', 'Datu Salibo',
        'Datu Saudi-Ampatuan', 'Datu Unsay', 'Gen. S.K. Pendatun', 'Guindulungan',
        'Mamasapano', 'Mangudadatu', 'Pagagawan', 'Pagalungan', 'Paglat', 'Pandag',
        'Rajah Buayan', 'Shariff Aguak', 'Shariff Saydona Mustapha', 'South Upi',
        'Sultan Sa Barongis', 'Talayan'
    ],
    'Maguindanao del Norte': [
        'Barira', 'Buldon', 'Datu Blah T. Sinsuat', 'Datu Odin Sinsuat',
        'Kabuntalan', 'Matanog', 'Northern Kabuntalan', 'Parang',
        'North Upi', 'Sultan Kudarat', 'Sultan Mastura', 'Talitay'
    ],
    'Cotabato City': [
        'Cotabato City'
    ],
    'Special Geographic Areas': [
        'Pahamuddin', 'Kadayangan', 'Nabalawag', 'Old Kaabakan',
        'Kapalawan', 'Malidegao', 'Tugunan', 'Ligawasan'
    ]
}

def safe_voter_id_upload(instance, filename):
    """
    Safely handle voter ID photo uploads by ensuring directories exist.
    Falls back to constituents directory if voter_id_photos cannot be created.
    """
    # Try primary path first
    primary_path = 'voter_id_photos/'
    full_primary_path = os.path.join(settings.MEDIA_ROOT, primary_path)
    
    # Try secondary path as fallback
    secondary_path = 'constituents/voter_id_photos/'
    full_secondary_path = os.path.join(settings.MEDIA_ROOT, secondary_path)
    
    # List of paths to try in order
    paths_to_try = [
        (primary_path, full_primary_path),
        (secondary_path, full_secondary_path),
        ('constituents/', os.path.join(settings.MEDIA_ROOT, 'constituents/')),  # Final fallback
    ]
    
    for upload_path, full_path in paths_to_try:
        try:
            # Ensure parent directory exists first
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, mode=0o755, exist_ok=True)
                
            # Create the target directory
            os.makedirs(full_path, mode=0o755, exist_ok=True)
            logger.info(f"Using voter ID photos directory: {full_path}")
            
            # Clean filename to avoid issues
            base, ext = os.path.splitext(filename)
            clean_filename = f"{instance.user.username}_voter_id{ext}"
            
            return os.path.join(upload_path, clean_filename)
            
        except PermissionError as e:
            logger.error(f"Permission denied creating directory {full_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error creating directory {full_path}: {e}")
            continue
    
    # If all paths fail, return a simple path and let Django handle it
    logger.error("All directory creation attempts failed, using simple path")
    return f"voter_id_{instance.user.username}_{filename}"
