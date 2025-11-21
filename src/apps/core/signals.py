from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from .utils import ensure_media_directories
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_media_directories(sender, **kwargs):
    """
    Create media directories after migrations are run.
    """
    if sender.name == 'apps.core':
        try:
            ensure_media_directories()
            logger.info("Media directories created successfully")
        except Exception as e:
            logger.warning(f"Could not create media directories: {e}")