from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.constituents.models import Constituent
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates missing Constituent profiles for existing users.'

    def handle(self, *args, **options):
        User = get_user_model()
        users_without_constituent = []

        self.stdout.write(self.style.SUCCESS('Starting to check for missing Constituent profiles...'))

        # Iterate through all users
        for user in User.objects.all():
            if not hasattr(user, 'constituent'):
                users_without_constituent.append(user)
        
        if not users_without_constituent:
            self.stdout.write(self.style.SUCCESS('No missing Constituent profiles found. All users have a linked profile.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(users_without_constituent)} users without a Constituent profile. Creating them now...'))

        for user in users_without_constituent:
            try:
                Constituent.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Successfully created Constituent profile for user: {user.username} (ID: {user.id})'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to create Constituent profile for user: {user.username} (ID: {user.id}) - Error: {e}'))
                logger.error(f"Error creating Constituent profile for user {user.username}: {e}", exc_info=True)

        self.stdout.write(self.style.SUCCESS('Finished checking and creating missing Constituent profiles.'))
